#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)

for tool in pdflatex; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "SKIP: $tool is required for table-legibility regression fixtures"
        exit 0
    fi
done

TEST_TMP=$(mktemp -d /tmp/arpipeline-table-legibility.XXXXXX)
trap 'rm -rf -- "$TEST_TMP"' EXIT

"$ROOT/setup.sh" "$TEST_TMP/deploy" --assemble-only --no-model-probe >"$TEST_TMP/setup.log"
PAPER="$TEST_TMP/deploy/paper"

write_doc() {
    local name=$1 body=$2 extra_packages=${3:-}
    {
        printf '%s\n' '\documentclass[11pt]{article}'
        # Match the deployed skeleton's important package order: arpipeline is
        # loaded early and installs its hooks at begin-document after later
        # table/graphics packages have defined their environments.
        printf '%s\n' '\usepackage[utf8]{inputenc}' '\usepackage{hyperref}' '\usepackage{arpipeline}'
        printf '%s\n' '\usepackage{amsmath}' '\usepackage{graphicx}' '\usepackage{booktabs}'
        [ -z "$extra_packages" ] || printf '%s\n' "$extra_packages"
        printf '%s\n' '\begin{document}'
        printf '%s\n' "$body"
        printf '%s\n' '\end{document}'
    } >"$PAPER/$name.tex"
}

expect_pass() {
    local name=$1
    if ! (cd "$PAPER" && pdflatex -interaction=nonstopmode -halt-on-error "$name.tex" >"$name.stdout" 2>&1); then
        echo "FAIL: $name should compile"
        tail -n 30 "$PAPER/$name.stdout"
        exit 1
    fi
    if grep -q 'ARPIPELINE-TABLE-LEGIBILITY-FAIL' "$PAPER/$name.log"; then
        echo "FAIL: $name emitted a legibility failure"
        exit 1
    fi
    echo "PASS: allowed — $name"
}

expect_fail() {
    local name=$1
    if (cd "$PAPER" && pdflatex -interaction=nonstopmode -halt-on-error "$name.tex" >"$name.stdout" 2>&1); then
        echo "FAIL: $name should have failed compilation"
        exit 1
    fi
    if ! grep -q 'ARPIPELINE-TABLE-LEGIBILITY-FAIL' "$PAPER/$name.log"; then
        echo "FAIL: $name failed for the wrong reason"
        tail -n 30 "$PAPER/$name.stdout"
        exit 1
    fi
    echo "PASS: rejected — $name"
}

write_doc normal '\begin{tabular}{ll}Normal & table\\\end{tabular}'
write_doc scriptsize '{\scriptsize\begin{tabular}{ll}Boundary & passes\\\end{tabular}}'
write_doc scaled_figure '\scalebox{0.1}{\rule{100pt}{20pt}}'
write_doc nested_scaled_figure '\scalebox{0.2}{\scalebox{0.2}{\rule{100pt}{20pt}}}'
write_doc upscaled_tiny '\scalebox{2}{\tiny\begin{tabular}{ll}Upscaled & readable\\\end{tabular}}'
write_doc scale_above_floor '\scalebox{0.8}{\begin{tabular}{ll}Still & readable\\\end{tabular}}'
write_doc adjustbox_noscale '\adjustbox{frame}{\begin{tabular}{ll}Framed & readable\\\end{tabular}}' '\usepackage{adjustbox}'
write_doc adjustbox_rotation '\adjustbox{rotate=90}{\begin{tabular}{llllllll}Readable&A&B&C&D&E&F&G\\\end{tabular}}' '\usepackage{adjustbox}'
write_doc adjustbox_environment_figure '\begin{adjustbox}{scale=0.2}\rule{100pt}{20pt}\end{adjustbox}' '\usepackage{adjustbox}'
write_doc nested_adjustbox_environment_figure '\begin{adjustbox}{frame}\begin{adjustbox}{scale=0.2}\rule{100pt}{20pt}\end{adjustbox}\end{adjustbox}' '\usepackage{adjustbox}'
write_doc equation_array '{\tiny$\begin{array}{cc}a&b\\c&d\end{array}$}'
write_doc transformed_equation '\begin{equation}\resizebox{.4\textwidth}{!}{$\begin{array}{rcl}a&=&b+c\\d&=&e+f\end{array}$}\end{equation}'

write_doc tiny '{\tiny\begin{tabular}{ll}Tiny & table\\\end{tabular}}'
write_doc resize '\resizebox{0.2\textwidth}{!}{\begin{tabular}{*{10}{c}}A&B&C&D&E&F&G&H&I&J\\\end{tabular}}'
write_doc resize_star '\resizebox*{0.2\textwidth}{!}{\begin{tabular}{*{10}{c}}A&B&C&D&E&F&G&H&I&J\\\end{tabular}}'
write_doc scale '\scalebox{0.2}{\begin{tabular}{*{10}{c}}A&B&C&D&E&F&G&H&I&J\\\end{tabular}}'
write_doc scale_vertical '\scalebox{1}[0.2]{\begin{tabular}{*{10}{c}}A&B&C&D&E&F&G&H&I&J\\\end{tabular}}'
write_doc nested_scale '\scalebox{0.8}{\scalebox{0.8}{\begin{tabular}{ll}Combined & too small\\\end{tabular}}}'
write_doc nested_scale_legal_factors '\scalebox{0.9}{\scalebox{0.9}{\begin{tabular}{ll}Opaque & composition\\\end{tabular}}}'
write_doc table_then_nested_figure '\scalebox{0.9}{\begin{tabular}{ll}Detected & before nested figure\\\end{tabular}\scalebox{0.2}{\rule{10pt}{10pt}}}'
write_doc semantic_table_array '\begin{table}\resizebox{0.2\textwidth}{!}{$\begin{array}{*{10}{c}}A&B&C&D&E&F&G&H&I&J\\\end{array}$}\end{table}'
write_doc adjustbox '\adjustbox{scale=0.2}{\begin{tabular}{*{10}{c}}A&B&C&D&E&F&G&H&I&J\\\end{tabular}}' '\usepackage{adjustbox}'
write_doc adjustbox_environment_table '\begin{adjustbox}{scale=0.9}\begin{tabular}{ll}Opaque & table transform\\\end{tabular}\end{adjustbox}' '\usepackage{adjustbox}'
write_doc nested_adjustbox_environment_table '\begin{adjustbox}{frame}\begin{adjustbox}{frame}\rule{10pt}{10pt}\end{adjustbox}\begin{tabular}{ll}Still inside & outer environment\\\end{tabular}\end{adjustbox}' '\usepackage{adjustbox}'
write_doc longtable_tiny '{\tiny\begin{longtable}{ll}Tiny & long table\\\end{longtable}}' '\usepackage{longtable}'
write_doc tabularx_tiny '{\tiny\begin{tabularx}{\textwidth}{XX}Tiny & trial-set table\\\end{tabularx}}' '\usepackage{tabularx}'

cat >"$PAPER/image-source.tex" <<'EOF'
\documentclass{article}
\pagestyle{empty}
\begin{document}\rule{20pt}{10pt}\end{document}
EOF
(cd "$PAPER" && pdflatex -interaction=nonstopmode -halt-on-error image-source.tex >/dev/null 2>&1)
write_doc image_table '\begin{table}\centering\includegraphics[width=.2\textwidth]{image-source.pdf}\caption{Image table}\end{table}'
write_doc native_icon '\begin{table}\centering\begin{tabular}{ll}Native & \includegraphics[width=10pt]{image-source.pdf}\\\end{tabular}\caption{Native table with icon}\end{table}'

for case_name in normal scriptsize scaled_figure nested_scaled_figure upscaled_tiny scale_above_floor adjustbox_noscale adjustbox_rotation adjustbox_environment_figure nested_adjustbox_environment_figure equation_array transformed_equation native_icon; do
    expect_pass "$case_name"
done

for case_name in tiny resize resize_star scale scale_vertical nested_scale nested_scale_legal_factors table_then_nested_figure semantic_table_array adjustbox adjustbox_environment_table nested_adjustbox_environment_table longtable_tiny tabularx_tiny image_table; do
    expect_fail "$case_name"
done

echo "All table-legibility fixtures passed."
