# WildClawBench skill runtime apt deps - offline debhouse

This directory holds the `.deb` packages that the agent container
(`wildclawbench-ubuntu:v1.3`) needs at runtime for the pdf/image/audio
skills, but which are NOT baked into the image.

The agent network is created with `--internal` (see
`src/utils/litellm_sidecar.py:272-307`), so `apt-get install` from the
container fails with `Temporary failure resolving 'archive.ubuntu.com'`.
This debhouse is `docker cp`'d into the container by
`src/utils/docker_utils.py::_install_apt_deps_from_debhouse` and then
installed offline with `dpkg -i /opt/wb_debs/*.deb`.

Target image: `wildclawbench-ubuntu:v1.3` (Ubuntu 22.04, linux/amd64).

## Packages staged (18 .deb files, ~34 MB)

Top-level skill deps (declared by `_BASELINE_SKILL_APT_PACKAGES` in
`src/utils/docker_utils.py`):

- `tesseract-ocr` 4.1.1-2.1build1 (OCR engine used by `image-extract` /
  `pdf-extract` skills via `pytesseract`)
- `poppler-utils` 22.02.0-2ubuntu0.12 (`pdftotext`, `pdfinfo` used by
  `pdf-extract` skill when PyMuPDF can't recover text)
- `unzip` 6.0-26ubuntu3.2 (used by skill scripts that need to inspect
  `.docx` / `.xlsx` / `.zip` bundles when the python parser is missing
  — observed in trajectories `925303a7-...` and `e2d2ce1d-...`)

Transitive deps required by the three top-level packages (resolved
against Ubuntu 22.04 and pruned against `wildclawbench-ubuntu:v1.3`):

- `libtesseract4`, `liblept5` (tesseract runtime)
- `tesseract-ocr-eng`, `tesseract-ocr-osd` (English + orientation data)
- `libpoppler118` (poppler runtime)
- `libgif7`, `liblcms2-2` (image codecs pulled in by leptonica)
- `fonts-croscore`, `fonts-freefont-otf`, `fonts-freefont-ttf`,
  `fonts-liberation`, `fonts-liberation2`, `fonts-texgyre`,
  `fonts-urw-base35`, `ttf-bitstream-vera` (font packages required by
  poppler/tesseract recommends; pulled in so `dpkg -i` doesn't break on
  missing fonts during postinst)

## Rebuild recipe

Step 1 - download every direct + transitive .deb for the three top-level
packages from Ubuntu 22.04:

```bash
docker run --rm --platform linux/amd64 \
  -v "$PWD/debhouse/skill-deps":/out \
  ubuntu:22.04 bash -c '
    apt-get update -qq
    apt-get install -y --no-install-recommends apt-rdepends >/dev/null
    cd /tmp && mkdir -p debs && cd debs
    for pkg in tesseract-ocr poppler-utils unzip; do
      for dep in $(apt-rdepends "$pkg" 2>/dev/null | grep -v "^ "); do
        apt-get download "$dep" 2>/dev/null || true
      done
    done
    mv *.deb /out/
  '
```

Step 2 - prune .debs that are already installed in
`wildclawbench-ubuntu:v1.3` so we only stage the truly missing ones:

```bash
comm -12 \
  <(ls debhouse/skill-deps/*.deb | sed 's|_.*||;s|.*/||' | sort -u) \
  <(docker run --rm wildclawbench-ubuntu:v1.3 \
      dpkg -l | awk '/^ii/ {print $2}' \
      | sed 's|:amd64||;s|:i386||' | sort -u) \
  | xargs -I{} rm debhouse/skill-deps/{}_*.deb
```

Step 3 - verify offline install against the real image:

```bash
docker run --rm --platform linux/amd64 \
  -v "$PWD/debhouse/skill-deps":/opt/wb_debs \
  wildclawbench-ubuntu:v1.3 bash -c '
    cd /opt/wb_debs
    DEBIAN_FRONTEND=noninteractive dpkg -i *.deb
    which tesseract pdftotext unzip
  '
```

Expected output: `/usr/bin/tesseract`, `/usr/bin/pdftotext`, `/usr/bin/unzip`.
