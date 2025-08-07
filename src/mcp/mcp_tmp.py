import json
import logging
import platform
import httpx
from fastmcp import FastMCP


mcp = FastMCP(name="system info mcp")


@mcp.tool()
def get_system_info() -> str:
    """
    Get system information
    """
    info: dict[str, str] = {
        "system": platform.system(),
        "platform": platform.platform(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
    }
    return json.dumps(info)


@mcp.tool()
def get_horoscope_info(type: str, time: str) -> dict:
    """Get horoscope information
    Args:
        type (str): 星座 aries, taurus, gemini, cancer, leo, virgo, libra, scorpio, sagittarius, capricorn, aquarius, pisces
        time (str): 时间 today, nextday, week, month

    Returns:
        str: 星座信息
    """
    logging.info("请求参数: type=%s, time=%s", type, time)
    url = f"https://api.vvhan.com/api/horoscope?type={type}&time={time}"
    response = httpx.get(url)
    return response.json()


if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8000)
