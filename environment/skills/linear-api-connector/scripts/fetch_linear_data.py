#!/usr/bin/env python3
"""CLI helper for reading Linear workspace data — issues, teams, users, projects, and cycles."""

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
    parser = argparse.ArgumentParser(description="Query a Linear API service")
    parser.add_argument("--teams", action="store_true",
                        help="List all teams")
    parser.add_argument("--team", metavar="TEAM_ID",
                        help="Fetch team details")
    parser.add_argument("--team-members", metavar="TEAM_ID",
                        help="List members of a team")
    parser.add_argument("--team-issues", metavar="TEAM_ID",
                        help="List issues for a team")
    parser.add_argument("--team-states", metavar="TEAM_ID",
                        help="List workflow states for a team")
    parser.add_argument("--users", action="store_true",
                        help="List all users")
    parser.add_argument("--user", metavar="USER_ID",
                        help="Fetch user details")
    parser.add_argument("--user-issues", metavar="USER_ID",
                        help="List issues assigned to a user")
    parser.add_argument("--issues", action="store_true",
                        help="List issues (combine with filters)")
    parser.add_argument("--issue", metavar="ISSUE_ID",
                        help="Fetch details for a specific issue")
    parser.add_argument("--search", metavar="QUERY",
                        help="Search issues by keyword")
    parser.add_argument("--projects", action="store_true",
                        help="List all projects")
    parser.add_argument("--project", metavar="PROJECT_ID",
                        help="Fetch project details")
    parser.add_argument("--project-issues", metavar="PROJECT_ID",
                        help="List issues for a project")
    parser.add_argument("--cycles", action="store_true",
                        help="List all cycles")
    parser.add_argument("--cycle", metavar="CYCLE_ID",
                        help="Fetch cycle details")
    parser.add_argument("--cycle-issues", metavar="CYCLE_ID",
                        help="List issues in a cycle")
    parser.add_argument("--labels", action="store_true",
                        help="List all labels")
    parser.add_argument("--comments", metavar="ISSUE_ID",
                        help="List comments for an issue")
    parser.add_argument("--stateId", metavar="STATE_ID",
                        help="Filter issues by workflow state")
    parser.add_argument("--assigneeId", metavar="USER_ID",
                        help="Filter issues by assignee")
    parser.add_argument("--projectId", metavar="PROJECT_ID",
                        help="Filter issues by project")
    parser.add_argument("--teamId", metavar="TEAM_ID",
                        help="Filter issues/cycles/labels by team")
    parser.add_argument("--priority", type=int,
                        help="Filter issues by priority (0-4)")
    parser.add_argument("--labelId", metavar="LABEL_ID",
                        help="Filter issues by label")
    parser.add_argument("--status", metavar="STATUS",
                        help="Filter cycles by status (current, past, upcoming)")
    parser.add_argument("--limit", type=int,
                        help="Maximum results to return")

    args = parser.parse_args()
    base_url = os.environ.get("LINEAR_API_URL", "http://localhost:8004")

    try:
        if args.teams:
            print_json(api_get(base_url, "/v1/teams"))
            return

        if args.team:
            print_json(api_get(base_url, f"/v1/teams/{args.team}"))
            return

        if args.team_members:
            print_json(api_get(base_url, f"/v1/teams/{args.team_members}/members"))
            return

        if args.team_issues:
            params = {}
            if args.limit:
                params["limit"] = str(args.limit)
            print_json(api_get(base_url, f"/v1/teams/{args.team_issues}/issues", params or None))
            return

        if args.team_states:
            print_json(api_get(base_url, f"/v1/teams/{args.team_states}/workflow-states"))
            return

        if args.users:
            print_json(api_get(base_url, "/v1/users"))
            return

        if args.user:
            print_json(api_get(base_url, f"/v1/users/{args.user}"))
            return

        if args.user_issues:
            params = {}
            if args.limit:
                params["limit"] = str(args.limit)
            print_json(api_get(base_url, f"/v1/users/{args.user_issues}/issues", params or None))
            return

        if args.issues:
            params = {}
            if args.stateId:
                params["stateId"] = args.stateId
            if args.assigneeId:
                params["assigneeId"] = args.assigneeId
            if args.projectId:
                params["projectId"] = args.projectId
            if args.teamId:
                params["teamId"] = args.teamId
            if args.priority is not None:
                params["priority"] = str(args.priority)
            if args.labelId:
                params["labelId"] = args.labelId
            if args.limit:
                params["limit"] = str(args.limit)
            print_json(api_get(base_url, "/v1/issues", params or None))
            return

        if args.issue:
            print_json(api_get(base_url, f"/v1/issues/{args.issue}"))
            return

        if args.search:
            params = {"q": args.search}
            if args.limit:
                params["limit"] = str(args.limit)
            print_json(api_get(base_url, "/v1/issues/search", params))
            return

        if args.projects:
            print_json(api_get(base_url, "/v1/projects"))
            return

        if args.project:
            print_json(api_get(base_url, f"/v1/projects/{args.project}"))
            return

        if args.project_issues:
            params = {}
            if args.limit:
                params["limit"] = str(args.limit)
            print_json(api_get(base_url, f"/v1/projects/{args.project_issues}/issues", params or None))
            return

        if args.cycles:
            params = {}
            if args.teamId:
                params["teamId"] = args.teamId
            if args.status:
                params["status"] = args.status
            if args.limit:
                params["limit"] = str(args.limit)
            print_json(api_get(base_url, "/v1/cycles", params or None))
            return

        if args.cycle:
            print_json(api_get(base_url, f"/v1/cycles/{args.cycle}"))
            return

        if args.cycle_issues:
            params = {}
            if args.limit:
                params["limit"] = str(args.limit)
            print_json(api_get(base_url, f"/v1/cycles/{args.cycle_issues}/issues", params or None))
            return

        if args.labels:
            params = {}
            if args.teamId:
                params["teamId"] = args.teamId
            if args.limit:
                params["limit"] = str(args.limit)
            print_json(api_get(base_url, "/v1/labels", params or None))
            return

        if args.comments:
            params = {}
            if args.limit:
                params["limit"] = str(args.limit)
            print_json(api_get(base_url, f"/v1/issues/{args.comments}/comments", params or None))
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
