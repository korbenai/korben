"""Linear API client and shared utilities."""

import os
import yaml
import logging
from typing import List, Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)


class LinearClient:
    """Client for interacting with Linear's GraphQL API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.linear.app/graphql"
        self.headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger(__name__)
    
    def _execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a GraphQL query against Linear's API"""
        self.logger.debug(f"Executing GraphQL query with variables: {variables}")
        
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            self.logger.debug(f"API response status: {response.status_code}")
            
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
            
            result = response.json()
            
            if "errors" in result:
                error_msg = f"GraphQL errors: {result['errors']}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
            
            self.logger.debug("GraphQL query executed successfully")
            return result["data"]
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {e}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_user_by_name(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by display name or name"""
        self.logger.info(f"Searching for user: {username}")
        
        query = """
        query GetUsers {
            users {
                nodes {
                    id
                    name
                    displayName
                    email
                }
            }
        }
        """
        
        data = self._execute_query(query)
        users = data["users"]["nodes"]
        self.logger.debug(f"Retrieved {len(users)} users from API")
        
        # Try to find user by displayName first, then by name, then by email prefix
        for user in users:
            if (user["displayName"] == username or 
                user["name"] == username or 
                user["email"].startswith(username)):
                self.logger.info(f"Found user: {user['displayName']} ({user['email']})")
                return user
        
        self.logger.warning(f"User '{username}' not found")
        return None
    
    def get_workflow_states(self) -> List[Dict[str, Any]]:
        """Get all workflow states"""
        self.logger.info("Fetching workflow states")
        
        query = """
        query GetWorkflowStates {
            workflowStates {
                nodes {
                    id
                    name
                    type
                    team {
                        id
                        name
                    }
                }
            }
        }
        """
        
        data = self._execute_query(query)
        states = data["workflowStates"]["nodes"]
        self.logger.debug(f"Retrieved {len(states)} workflow states")
        return states
    
    def get_issues_by_user_and_states(self, user_id: str, state_ids: List[str]) -> List[Dict[str, Any]]:
        """Get issues assigned to a user with specific workflow states"""
        self.logger.info(f"Fetching issues for user {user_id} with {len(state_ids)} states")
        
        query = """
        query GetIssues($filter: IssueFilter) {
            issues(filter: $filter) {
                nodes {
                    id
                    identifier
                    title
                    description
                    priority
                    estimate
                    createdAt
                    updatedAt
                    dueDate
                    url
                    state {
                        id
                        name
                        type
                    }
                    assignee {
                        id
                        name
                        displayName
                        email
                    }
                    team {
                        id
                        name
                    }
                    project {
                        id
                        name
                    }
                    labels {
                        nodes {
                            id
                            name
                            color
                        }
                    }
                }
            }
        }
        """
        
        variables = {
            "filter": {
                "assignee": {"id": {"eq": user_id}},
                "state": {"id": {"in": state_ids}}
            }
        }
        
        data = self._execute_query(query, variables)
        issues = data["issues"]["nodes"]
        self.logger.info(f"Retrieved {len(issues)} issues")
        return issues


def load_linear_config():
    """Load Linear configuration from YAML file in plugin directory."""
    # Config lives in the plugin directory
    config_path = os.path.join(os.path.dirname(__file__), 'config.yml')
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"No config file found at: {config_path}\n"
            f"Please copy config.yml.example to config.yml in the linear plugin:\n"
            f"  cp src/plugins/linear/config.yml.example src/plugins/linear/config.yml"
        )
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


def format_issues_output(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format issues for output with simplified structure."""
    output_data = []
    
    for issue in issues:
        issue_data = {
            "id": issue["id"],
            "identifier": issue["identifier"],
            "name": issue["title"],
            "description": issue.get("description"),
            "status": issue["state"]["name"],
            "url": issue["url"],
            "priority": issue.get("priority"),
            "labels": [label["name"] for label in issue["labels"]["nodes"]],
            "team": issue["team"]["name"] if issue.get("team") else None,
            "project": issue["project"]["name"] if issue.get("project") else None,
            "dueDate": issue.get("dueDate"),
            "createdAt": issue.get("createdAt"),
            "updatedAt": issue.get("updatedAt")
        }
        output_data.append(issue_data)
    
    return output_data

