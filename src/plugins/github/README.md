# GitHub Plugin

The GitHub plugin provides tasks for interacting with GitHub's API, currently focused on creating gists from files and directories.

## Features

- **Create Gist from File**: Create a GitHub gist from a single file
- **Create Gist from Directory**: Create a GitHub gist from all files in a directory

## Configuration

### 1. Set Up GitHub API Key

Create a GitHub Personal Access Token (PAT):

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" (classic)
3. Give it a descriptive name (e.g., "Korben Gist Creator")
4. Select the `gist` scope
5. Click "Generate token"
6. Copy the token and save it securely

Set the token as an environment variable:

```bash
export GITHUB_API_KEY="your_token_here"
```

Or add it to your shell profile (`~/.zshrc`, `~/.bashrc`, etc.):

```bash
echo 'export GITHUB_API_KEY="your_token_here"' >> ~/.zshrc
source ~/.zshrc
```

### 2. Create Plugin Configuration (Optional)

Copy the example config:

```bash
cp src/plugins/github/config.yml.example src/plugins/github/config.yml
```

Edit `config.yml` to customize default settings:

```yaml
variables:
  default_description: "Gist created by Korben"
  public: true
```

## Tasks

### create_gist_from_file

Create a GitHub gist from a single file.

**Parameters:**
- `file_path` (required): Path to the file to create a gist from
- `description` (optional): Description for the gist (default: from config or "Gist created by Korben")
- `public` (optional): Whether the gist should be public - true or false (default: true)

**Examples:**

```bash
# Create a public gist from a file
pdm run python3 ./korben.py --task create_gist_from_file \
  --file_path /path/to/script.py \
  --description "My Python script"

# Create a secret gist
pdm run python3 ./korben.py --task create_gist_from_file \
  --file_path /path/to/secret.txt \
  --description "Private notes" \
  --public false

# Use default description from config
pdm run python3 ./korben.py --task create_gist_from_file \
  --file_path ~/Documents/notes.md
```

**Returns:**
- Success: URL of the created gist
- Error: Error message describing the issue

### create_gist_from_directory

Create a GitHub gist from all text files in a directory.

**Parameters:**
- `directory_path` (required): Path to the directory containing files
- `description` (optional): Description for the gist (default: from config or "Gist created by Korben")
- `public` (optional): Whether the gist should be public - true or false (default: true)

**Examples:**

```bash
# Create a gist from all files in a directory
pdm run python3 ./korben.py --task create_gist_from_directory \
  --directory_path /path/to/project \
  --description "Project files"

# Create a secret gist from directory
pdm run python3 ./korben.py --task create_gist_from_directory \
  --directory_path ~/config \
  --description "Configuration files" \
  --public false
```

**Notes:**
- Only text files are included; binary files are automatically skipped
- All files in the directory (not subdirectories) will be added to the gist
- Each file maintains its original filename in the gist

**Returns:**
- Success: URL of the created gist with file count
- Error: Error message describing the issue

## Error Handling

The plugin handles various error conditions:

- **Missing API Key**: Returns error if `GITHUB_API_KEY` is not set
- **File Not Found**: Returns error if the specified file or directory doesn't exist
- **No Files**: Returns error if directory contains no readable text files
- **API Errors**: Returns detailed error message if GitHub API request fails

## Common Issues

### Authentication Failed

If you see authentication errors:
1. Verify your `GITHUB_API_KEY` is set correctly
2. Check that the token hasn't expired
3. Ensure the token has the `gist` scope enabled

### File Not Found

Make sure to provide the full path to files or directories. The plugin will expand `~` for home directory.

### Binary Files Skipped

When creating gists from directories, binary files are automatically skipped with a warning in the logs. Only text files will be included in the gist.

## Integration with Other Plugins

The GitHub plugin can be combined with other Korben plugins:

```bash
# Example: Share a file via gist after generating it
pdm run python3 ./korben.py --task some_task_that_creates_file
pdm run python3 ./korben.py --task create_gist_from_file --file_path /path/to/generated/file.txt
```

## API Documentation

For more information about GitHub's Gist API:
- [GitHub Gist API Documentation](https://docs.github.com/en/rest/gists)
- [Creating Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

