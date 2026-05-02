"""Shared constants."""

DEFAULT_USER_AGENT = "HCrawler/7.0 (+authorized-security-research)"

SECURITY_HEADERS = [
    "content-security-policy",
    "strict-transport-security",
    "x-frame-options",
    "x-content-type-options",
    "referrer-policy",
    "permissions-policy",
    "cross-origin-opener-policy",
    "cross-origin-resource-policy",
    "cross-origin-embedder-policy",
]

BINARY_EXTENSIONS = (
    "zip", "tar", "gz", "rar", "7z", "jpg", "jpeg", "png", "gif", "webp", "svg",
    "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "mp4", "mp3", "avi",
    "mov", "iso", "dmg", "exe", "msi", "woff", "woff2", "ttf", "eot"
)

SENSITIVE_PATH_HINTS = [
    ".env",
    ".env.local",
    ".git/HEAD",
    ".svn/entries",
    "backup.zip",
    "backup.tar.gz",
    "dump.sql",
    "db.sql",
    "database.sql",
    "config.php",
    "config.json",
    "phpinfo.php",
    "server-status",
    "admin",
    "login",
    "debug",
    "actuator",
    "actuator/env",
    "swagger",
    "swagger.json",
    "openapi.json",
    "api/docs",
]

DEFAULT_DENY_PATTERNS = [
    r"logout",
    r"delete",
    r"remove",
    r"signout",
    r"cart",
    r"checkout",
]
