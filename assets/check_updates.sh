#!/bin/bash

# Parse middels Conky: ${execi 1000 assets/check_updates.sh}

# Configuratie
CACHE_DIR="/tmp"
CACHE_DURATION=3600 # 1 uur in seconden

# Cachebestanden worden dynamisch bepaald op basis van OS
CACHE_FILE_APT="$CACHE_DIR/package_updates_apt.txt"
CACHE_FILE_PACMAN="$CACHE_DIR/package_updates_pacman.txt"
CACHE_FILE_AUR="$CACHE_DIR/package_updates_aur.txt"
CACHE_FILE_DNF="$CACHE_DIR/package_updates_dnf.txt"

# Functie om de laatste wijzigingstijd van een bestand te krijgen
last_update() {
    local file="$1"
    if [[ -f "$file" ]]; then
        stat -c %Y "$file" 2>/dev/null || echo 0
    else
        echo 0
    fi
}

# Functie om het besturingssysteem te detecteren
detect_os() {
    if [[ -f /etc/os-release ]]; then
        # shellcheck disable=SC1091
        source /etc/os-release
        case "$ID" in
            "debian"|"ubuntu")
                echo "debian"
                ;;
            "arch")
                echo "arch"
                ;;
            "fedora")
                echo "fedora"
                ;;
            *)
                echo "unsupported"
                ;;
        esac
    else
        echo "unsupported"
    fi
}

# Functie om cache bij te werken op basis van OS
update_cache() {
    local os="$1"
    local current_time
    current_time=$(date +%s)

    case "$os" in
        "debian")
            if [[ $((current_time - $(last_update "$CACHE_FILE_APT"))) -gt $CACHE_DURATION ]]; then
                apt list --upgradable > "$CACHE_FILE_APT" 2>/dev/null
            fi
            ;;
        "arch")
            if [[ $((current_time - $(last_update "$CACHE_FILE_PACMAN"))) -gt $CACHE_DURATION ]]; then
                checkupdates > "$CACHE_FILE_PACMAN" 2>/dev/null
            fi
            if [[ $((current_time - $(last_update "$CACHE_FILE_AUR"))) -gt $CACHE_DURATION ]]; then
                if command -v yay >/dev/null 2>&1; then
                    yay -Qua > "$CACHE_FILE_AUR" 2>/dev/null
                elif command -v paru >/dev/null 2>&1; then
                    paru -Qua > "$CACHE_FILE_AUR" 2>/dev/null
                fi
            fi
            ;;
        "fedora")
            if [[ $((current_time - $(last_update "$CACHE_FILE_DNF"))) -gt $CACHE_DURATION ]]; then
                dnf check-update --refresh > "$CACHE_FILE_DNF" 2>/dev/null
            fi
            ;;
        *)
            echo "Geen ondersteunde pakketmanager gevonden"
            exit 1
            ;;
    esac
}

# Functie om pakketupdates te laden en te tellen
load_package_lines() {
    local os
    os=$(detect_os)
    local original_lines=()
    local update_count

    # Update cache voor het gedetecteerde OS
    update_cache "$os"

    # Verwerk updates op basis van OS
    case "$os" in
        "debian")
            if [[ -f "$CACHE_FILE_APT" ]]; then
                while IFS= read -r line; do
                    # Sla de eerste regel over ("Listing...")
                    if [[ ! "$line" =~ ^Listing... ]]; then
                        # Haal pakketnaam op voor de eerste slash
                        package_name=$(echo "$line" | grep -oP '^[^/]+' | sed 's|/.*||')
                        if [[ -n "$package_name" ]]; then
                            # Beperk lengte tot 20 karakters
                            if [[ ${#package_name} -gt 20 ]]; then
                                package_name="${package_name:0:17}..."
                            fi
                            original_lines+=("$package_name")
                        fi
                    fi
                done < "$CACHE_FILE_APT"
            fi
            ;;
        "arch")
            if [[ -f "$CACHE_FILE_PACMAN" ]]; then
                while IFS= read -r line; do
                    package_name=$(echo "$line" | awk '{print $1}')
                    if [[ -n "$package_name" ]]; then
                        original_lines+=("$package_name")
                    fi
                done < "$CACHE_FILE_PACMAN"
            fi
            if [[ -f "$CACHE_FILE_AUR" ]]; then
                if command -v yay >/dev/null 2>&1 || command -v paru >/dev/null 2>&1; then
                    while IFS= read -r line; do
                        package_name=$(echo "$line" | awk '{print $1}')
                        if [[ -n "$package_name" ]]; then
                            original_lines+=("$package_name")
                        fi
                    done < "$CACHE_FILE_AUR"
                fi
            fi
            ;;
        "fedora")
            if [[ -f "$CACHE_FILE_DNF" ]]; then
                # Sla regels over die geen pakketnamen bevatten (bijv. lege regels, headers)
                while IFS= read -r line; do
                    # Controleer of de regel een pakketnaam bevat (begint met een woord, gevolgd door versie)
                    if [[ "$line" =~ ^[a-zA-Z0-9._-]+[[:space:]]+[0-9] ]]; then
                        package_name=$(echo "$line" | awk '{print $1}')
                        if [[ -n "$package_name" ]]; then
                            # Beperk lengte tot 20 karakters
                            if [[ ${#package_name} -gt 20 ]]; then
                                package_name="${package_name:0:17}..."
                            fi
                            original_lines+=("$package_name")
                        fi
                    fi
                done < "$CACHE_FILE_DNF"
            fi
            ;;
        *)
            echo "Geen ondersteunde pakketmanager gevonden"
            exit 1
            ;;
    esac

    # Tel het aantal updates
    update_count=${#original_lines[@]}

    # Geef resultaat
    if [[ $update_count -eq 0 ]]; then
        echo "System is up-to-date"
    else
        echo "$update_count updates available"
    fi
}

# Hoofdfunctie om updates te tonen
updates_block() {
    load_package_lines
}

# Roep de functie aan
updates_block