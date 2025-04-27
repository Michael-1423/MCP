from mcp.server.fastmcp import FastMCP
import os
import shutil
from typing import List, Optional

mcp = FastMCP("FileSystemMCP")

@mcp.tool()
def list_directory(path: str) -> List[str]:
    """
    List contents of a directory.
    
    Args:
        path: Path to directory
        
    Returns:
        List of file and directory names in the specified directory
    """
    if not os.path.exists(path):
        raise ValueError(f"Path does not exist: {path}")
    if not os.path.isdir(path):
        raise ValueError(f"Path is not a directory: {path}")
    
    return os.listdir(path)

@mcp.tool()
def read_file(path: str) -> str:
    """
    Read contents of a file.
    
    Args:
        path: Path to file
        
    Returns:
        Contents of the file as a string
    """
    if not os.path.exists(path):
        raise ValueError(f"File does not exist: {path}")
    if not os.path.isfile(path):
        raise ValueError(f"Path is not a file: {path}")
    
    with open(path, 'r') as file:
        return file.read()

@mcp.tool()
def write_file(path: str, content: str) -> bool:
    """
    Write content to a file.
    
    Args:
        path: Path to file
        content: Content to write
        
    Returns:
        True if successful
    """
    with open(path, 'w') as file:
        file.write(content)
    return True

@mcp.tool()
def delete_file(path: str) -> bool:
    """
    Delete a file.
    
    Args:
        path: Path to file
        
    Returns:
        True if successful
    """
    if not os.path.exists(path):
        raise ValueError(f"File does not exist: {path}")
    if not os.path.isfile(path):
        raise ValueError(f"Path is not a file: {path}")
    
    os.remove(path)
    return True

@mcp.tool()
def create_directory(path: str) -> bool:
    """
    Create a directory.
    
    Args:
        path: Path to new directory
        
    Returns:
        True if successful
    """
    if os.path.exists(path):
        raise ValueError(f"Path already exists: {path}")
    
    os.makedirs(path)
    return True

@mcp.tool()
def delete_directory(path: str, recursive: bool = False) -> bool:
    """
    Delete a directory.
    
    Args:
        path: Path to directory
        recursive: If True, recursively delete directory and its contents
        
    Returns:
        True if successful
    """
    if not os.path.exists(path):
        raise ValueError(f"Directory does not exist: {path}")
    if not os.path.isdir(path):
        raise ValueError(f"Path is not a directory: {path}")
    
    if recursive:
        shutil.rmtree(path)
    else:
        os.rmdir(path)
    return True

@mcp.tool()
def file_exists(path: str) -> bool:
    """
    Check if a file exists.
    
    Args:
        path: Path to file
        
    Returns:
        True if file exists, False otherwise
    """
    return os.path.isfile(path)

@mcp.tool()
def directory_exists(path: str) -> bool:
    """
    Check if a directory exists.
    
    Args:
        path: Path to directory
        
    Returns:
        True if directory exists, False otherwise
    """
    return os.path.isdir(path)

@mcp.tool()
def copy_file(source: str, destination: str) -> bool:
    """
    Copy a file from source to destination.
    
    Args:
        source: Source file path
        destination: Destination file path
        
    Returns:
        True if successful
    """
    if not os.path.exists(source):
        raise ValueError(f"Source file does not exist: {source}")
    if not os.path.isfile(source):
        raise ValueError(f"Source path is not a file: {source}")
    
    shutil.copy2(source, destination)
    return True

@mcp.tool()
def move_file(source: str, destination: str) -> bool:
    """
    Move a file from source to destination.
    
    Args:
        source: Source file path
        destination: Destination file path
        
    Returns:
        True if successful
    """
    if not os.path.exists(source):
        raise ValueError(f"Source file does not exist: {source}")
    if not os.path.isfile(source):
        raise ValueError(f"Source path is not a file: {source}")
    
    shutil.move(source, destination)
    return True

@mcp.tool()
def get_file_size(path: str) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        path: Path to file
        
    Returns:
        Size of the file in bytes
    """
    if not os.path.exists(path):
        raise ValueError(f"File does not exist: {path}")
    if not os.path.isfile(path):
        raise ValueError(f"Path is not a file: {path}")
    
    return os.path.getsize(path)

@mcp.resource("file://{path}")
def get_file_info(path: str) -> dict:
    """
    Get information about a file.
    
    Args:
        path: Path to file
        
    Returns:
        Dictionary with file information
    """
    if not os.path.exists(path):
        raise ValueError(f"Path does not exist: {path}")
    
    stat_info = os.stat(path)
    return {
        "path": path,
        "size": stat_info.st_size,
        "is_file": os.path.isfile(path),
        "is_dir": os.path.isdir(path),
        "modified_time": stat_info.st_mtime,
        "created_time": stat_info.st_ctime,
        "accessed_time": stat_info.st_atime
    }

@mcp.resource("dir://{path}")
def get_directory_info(path: str) -> dict:
    """
    Get information about a directory.
    
    Args:
        path: Path to directory
        
    Returns:
        Dictionary with directory information
    """
    if not os.path.exists(path):
        raise ValueError(f"Path does not exist: {path}")
    if not os.path.isdir(path):
        raise ValueError(f"Path is not a directory: {path}")
    
    contents = os.listdir(path)
    files = [f for f in contents if os.path.isfile(os.path.join(path, f))]
    dirs = [d for d in contents if os.path.isdir(os.path.join(path, d))]
    
    return {
        "path": path,
        "files_count": len(files),
        "dirs_count": len(dirs),
        "files": files,
        "directories": dirs
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")