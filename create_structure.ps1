$ErrorActionPreference = "Stop"

$base = "c:\Users\lenovo\StreamForge\StreamForge-Project\rocksdb_state"
New-Item -ItemType Directory -Force -Path "$base" | Out-Null
New-Item -ItemType Directory -Force -Path "$base\rocksdb_state" | Out-Null
New-Item -ItemType Directory -Force -Path "$base\tests" | Out-Null
New-Item -ItemType Directory -Force -Path "$base\docs" | Out-Null
New-Item -ItemType Directory -Force -Path "$base\examples" | Out-Null
New-Item -ItemType Directory -Force -Path "$base\scripts" | Out-Null

$root_files = @("requirements.txt", "pyproject.toml", "README.md", "LICENSE", ".gitignore")
foreach ($f in $root_files) {
    New-Item -ItemType File -Force -Path "$base\$f" | Out-Null
}

$pkg = "$base\rocksdb_state"
New-Item -ItemType File -Force -Path "$pkg\__init__.py" | Out-Null

$dirs = @("config", "database", "models", "serialization", "storage", "aggregation", "recovery", "cleanup", "health", "logging", "exceptions", "utils")
foreach ($d in $dirs) {
    New-Item -ItemType Directory -Force -Path "$pkg\$d" | Out-Null
    New-Item -ItemType File -Force -Path "$pkg\$d\__init__.py" | Out-Null
}

New-Item -ItemType File -Force -Path "$pkg\config\config.py" | Out-Null
New-Item -ItemType File -Force -Path "$pkg\database\database_manager.py" | Out-Null
New-Item -ItemType File -Force -Path "$pkg\database\initializer.py" | Out-Null
New-Item -ItemType File -Force -Path "$pkg\models\truck_state.py" | Out-Null
New-Item -ItemType File -Force -Path "$pkg\serialization\serializer.py" | Out-Null
New-Item -ItemType File -Force -Path "$pkg\serialization\deserializer.py" | Out-Null
New-Item -ItemType File -Force -Path "$pkg\storage\crud.py" | Out-Null
New-Item -ItemType File -Force -Path "$pkg\storage\key_manager.py" | Out-Null
New-Item -ItemType File -Force -Path "$pkg\aggregation\aggregator.py" | Out-Null
New-Item -ItemType File -Force -Path "$pkg\recovery\recovery_manager.py" | Out-Null
New-Item -ItemType File -Force -Path "$pkg\cleanup\cleanup_manager.py" | Out-Null
New-Item -ItemType File -Force -Path "$pkg\health\health_check.py" | Out-Null
New-Item -ItemType File -Force -Path "$pkg\logging\logger.py" | Out-Null
New-Item -ItemType File -Force -Path "$pkg\exceptions\exceptions.py" | Out-Null
New-Item -ItemType File -Force -Path "$pkg\utils\helpers.py" | Out-Null

$tests = "$base\tests"
$test_files = @("test_config.py", "test_database.py", "test_serializer.py", "test_deserializer.py", "test_key_manager.py", "test_crud.py", "test_aggregation.py", "test_recovery.py", "test_cleanup.py", "test_health.py", "test_integration.py")
foreach ($t in $test_files) {
    New-Item -ItemType File -Force -Path "$tests\$t" | Out-Null
}

$docs = "$base\docs"
$doc_files = @("PRD.md", "TRD.md", "PDO.md", "API.md", "Architecture.md", "Deployment.md", "Testing.md")
foreach ($d in $doc_files) {
    New-Item -ItemType File -Force -Path "$docs\$d" | Out-Null
}

$examples = "$base\examples"
$example_files = @("basic_usage.py", "crud_demo.py", "recovery_demo.py", "cleanup_demo.py")
foreach ($e in $example_files) {
    New-Item -ItemType File -Force -Path "$examples\$e" | Out-Null
}

$scripts = "$base\scripts"
$script_files = @("initialize_database.py", "reset_database.py", "benchmark.py", "run_tests.py")
foreach ($s in $script_files) {
    New-Item -ItemType File -Force -Path "$scripts\$s" | Out-Null
}

Write-Output "Project structure successfully created!"
