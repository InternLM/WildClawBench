#!/usr/bin/env python3
"""CLI helper for reading Google Classroom data — courses, coursework, submissions, students, and announcements."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse


def api_get(base_url, path, params=None):
    url = f"{base_url}{path}"
    if params:
        filtered = {k: v for k, v in params.items() if v is not None}
        if filtered:
            url += "?" + urllib.parse.urlencode(filtered)
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def print_json(data):
    print(json.dumps(data, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Query a Google Classroom API service")
    parser.add_argument("--courses", action="store_true",
                        help="List all courses")
    parser.add_argument("--course", metavar="COURSE_ID",
                        help="Fetch details for a specific course")
    parser.add_argument("--coursework", metavar="COURSE_ID",
                        help="List coursework for a course")
    parser.add_argument("--get-coursework", metavar="COURSEWORK_ID",
                        help="Fetch a specific coursework item (requires --course-id)")
    parser.add_argument("--submissions", metavar="COURSEWORK_ID",
                        help="List submissions for a coursework item (requires --course-id)")
    parser.add_argument("--students", metavar="COURSE_ID",
                        help="List students in a course")
    parser.add_argument("--teachers", metavar="COURSE_ID",
                        help="List teachers in a course")
    parser.add_argument("--topics", metavar="COURSE_ID",
                        help="List topics for a course")
    parser.add_argument("--announcements", metavar="COURSE_ID",
                        help="List announcements for a course")
    parser.add_argument("--materials", metavar="COURSE_ID",
                        help="List course work materials for a course")
    parser.add_argument("--course-id", metavar="COURSE_ID",
                        help="Course ID (used with --get-coursework and --submissions)")
    parser.add_argument("--course-states", metavar="STATES",
                        help="Filter courses by state (ACTIVE, ARCHIVED)")
    parser.add_argument("--topic-id", metavar="TOPIC_ID",
                        help="Filter coursework by topic ID")
    parser.add_argument("--states", metavar="STATES",
                        help="Filter submissions by state (TURNED_IN, RETURNED, NEW)")
    parser.add_argument("--late", action="store_true",
                        help="Filter for late submissions only")
    parser.add_argument("--page-size", type=int,
                        help="Maximum results to return")

    args = parser.parse_args()
    base_url = os.environ.get("GOOGLE_CLASSROOM_API_URL", "http://localhost:8002")

    try:
        if args.courses:
            params = {}
            if args.course_states:
                params["courseStates"] = args.course_states
            if args.page_size:
                params["pageSize"] = str(args.page_size)
            print_json(api_get(base_url, "/v1/courses", params or None))
            return

        if args.course:
            print_json(api_get(base_url, f"/v1/courses/{args.course}"))
            return

        if args.coursework:
            params = {}
            if args.topic_id:
                params["topicId"] = args.topic_id
            if args.page_size:
                params["pageSize"] = str(args.page_size)
            print_json(api_get(base_url, f"/v1/courses/{args.coursework}/courseWork", params or None))
            return

        if args.get_coursework:
            course_id = args.course_id or "course_001"
            print_json(api_get(base_url, f"/v1/courses/{course_id}/courseWork/{args.get_coursework}"))
            return

        if args.submissions:
            course_id = args.course_id or "course_001"
            params = {}
            if args.states:
                params["states"] = args.states
            if args.late:
                params["late"] = "true"
            if args.page_size:
                params["pageSize"] = str(args.page_size)
            print_json(api_get(base_url, f"/v1/courses/{course_id}/courseWork/{args.submissions}/studentSubmissions", params or None))
            return

        if args.students:
            params = {}
            if args.page_size:
                params["pageSize"] = str(args.page_size)
            print_json(api_get(base_url, f"/v1/courses/{args.students}/students", params or None))
            return

        if args.teachers:
            print_json(api_get(base_url, f"/v1/courses/{args.teachers}/teachers"))
            return

        if args.topics:
            print_json(api_get(base_url, f"/v1/courses/{args.topics}/topics"))
            return

        if args.announcements:
            params = {}
            if args.page_size:
                params["pageSize"] = str(args.page_size)
            print_json(api_get(base_url, f"/v1/courses/{args.announcements}/announcements", params or None))
            return

        if args.materials:
            print_json(api_get(base_url, f"/v1/courses/{args.materials}/courseWorkMaterials"))
            return

        parser.print_help()

    except urllib.error.HTTPError as exc:
        print(f"HTTP {exc.code}: {exc.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as exc:
        print(f"Connection error: {exc.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
