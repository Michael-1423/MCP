from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo")

@mcp.tool()
def add(a: int , b: int) -> int:
    """Add Two Numbers"""

    return a + b

@mcp.resource("greeting://{name}")
def get_greeting(name : str)->str:
    """Get a greeting message"""
    return f"Hello, {name}!"

if __name__=="__main__":
    mcp.run(transport="stdio")