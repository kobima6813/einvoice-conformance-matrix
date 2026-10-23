#!/usr/bin/env bash
# usage: generators/zugferd-csharp/run.sh <corpus_dir> <out_dir>   (needs .NET 8 SDK)
set -euo pipefail; H="$(cd "$(dirname "$0")" && pwd)"
dotnet run --project "$H/GenZ.csproj" -c Release -- "$1/ref_en16931_rounding.json" "$2"
