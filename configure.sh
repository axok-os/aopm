#!/usr/bin/env bash

info() {
    local msg="$1"
    sleep 0.1
    echo -e "=> \033[36m[INFO]\033[0m: $msg"
}

success() {
    local msg="$1"
    sleep 0.1
    echo -e "==> \033[32m[SUCCESS]\033[0m: $msg"
}

warn() {
    local msg="$1"
    sleep 0.1
    echo -e "=> \033[33m[WARNING]\033[0m: $msg"
}

error() {
    local msg="$1"
    sleep 0.1
    echo -e "==> \033[31m[ERROR]\033[0m: $msg"
}

# global variables
prefix="none"
with_aopkg="true"
config_dir="none"
var_dir="none"

# parse
for arg in "$@"; do
    case $arg in
        --prefix=*)
            prefix="${arg#*=}"
            info "Parameter: prefix=$prefix"
            shift
            ;;
        --with-aopkg=*)
            with_aopkg="${arg#*=}"
            info "Parameter: with-aopkg=$with_aopkg"
            shift
            ;;
        --config-dir=*)
            config_dir="${arg#*=}"
            info "Parameter: config-dir=$config_dir"
            shift
            ;;
        --var-dir=*)
            var_dir="${arg#*=}"
            info "Parameter: var-dir=$var_dir"
            shift
            ;;
        *)
            error "Invalid option $arg :("
            exit 1
    esac
done

info "Checking dependencies..."

info "Searching for: 'build'..."
if pip show build &>/dev/null; then
    success "'build' found!"
else
    error "Cant found: 'build' :("
    exit 1
fi

info "Searching for: 'python3'..."
if command -v python3 &>/dev/null; then
    success "'python3' found!"
else
    error "Cant found: 'python3' :("
    exit 1
fi

info "Searching for 'pip'..."
if command -v pip &>/dev/null; then
    success "'pip' found1"
else
    error "Cant found: 'pip' :("
    exit 1
fi

success "All dependencies checked!"
info "Checking variables..."
if [ "$prefix" == "none" ]; then
    error "The variable: 'prefix' is not defined :("
    exit 1
fi

if [ "$config_dir" == "none" ]; then
    error "The variable: 'config-dir' is not defined :("
    exit 1
fi

if [ "$lib_dir" == "none" ]; then
    error "The variable: 'lib-dir' is not defined :("
    exit 1
fi

if [ "$var_dir" == "none" ]; then
    error "The variable: 'var-dir' is not defined :("
    exit 1
fi

success "All variables checked!"
info "Configuring files..."

# src/core.py
if sed -i "s|^config_path = \".*\"|config_path = \"$config_dir\"|" src/core.py; then
    success "src/core.py configured!"
fi

# configs/aopm.conf
if sed -i "s|^[[:space:]]*repos_path *= *.*|repos_path = ${prefix}/share/aopm/repos|" configs/aopm.conf; then
    :
fi

if sed -i "s|^[[:space:]]*modules_path *= *.*|modules_path = ${prefix}/share/aopm/modules|" configs/aopm.conf; then
    :
fi

if sed -i "s|^[[:space:]]*repos_index_path *= *.*|repos_index_path = ${prefix}/lib/aopm/repos|" configs/aopm.conf; then
    :
fi

if sed -i "s|^[[:space:]]*keys_path *= *.*|keys_path = ${prefix}/share/aopm/keys|" configs/aopm.conf; then
    :
fi

if sed -i "s|^[[:space:]]*packages_path *= *.*|packages_path = ${var_dir}/packages|" configs/aopm.conf; then
    success "configs/aopm.conf configured!"
fi

info "Generating .config file..."
{
    echo "prefix = $prefix"
    echo "with-aopkg = $with_aopkg"
    echo "config-dir = $config_dir"
    echo "var-dir = $var_dir"
    echo "static = $static"
} > .config

success "File '.config' generated!"
exit 0