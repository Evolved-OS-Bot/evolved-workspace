<?php
// Blocksy Child Theme — The Evolved

add_action("wp_enqueue_scripts", "evolved_enqueue_styles");
function evolved_enqueue_styles() {
    wp_enqueue_style(
        "blocksy-parent-style",
        get_template_directory_uri() . "/style.css"
    );
}

add_action("wp_enqueue_scripts", "evolved_enqueue_homepage_scripts");
function evolved_enqueue_homepage_scripts() {
    if (!is_front_page()) return;
    wp_enqueue_script("gsap", "https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js", [], null, true);
    wp_enqueue_script("gsap-scrolltrigger", "https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js", ["gsap"], null, true);
    wp_enqueue_script("chartjs", "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js", [], null, true);
    wp_enqueue_script("evolved-homepage", get_stylesheet_directory_uri() . "/js/homepage.js", ["gsap", "gsap-scrolltrigger", "chartjs"], "59.0", true);
}

add_action("init", "evolved_register_results_cpt");
function evolved_register_results_cpt() {
    register_post_type("results", [
        "labels"       => ["name" => "Results", "singular_name" => "Result", "add_new_item" => "Add New Result", "edit_item" => "Edit Result"],
        "public"       => true,
        "has_archive"  => true,
        "rewrite"      => ["slug" => "results"],
        "supports"     => ["title", "editor", "thumbnail", "custom-fields", "excerpt"],
        "show_in_rest" => true,
        "menu_icon"    => "dashicons-awards",
    ]);
    register_taxonomy("goal", "results", [
        "label"        => "Goal",
        "rewrite"      => ["slug" => "results/goal"],
        "public"       => true,
        "hierarchical" => false,
        "show_in_rest" => true,
    ]);
    register_taxonomy("life_stage", "results", [
        "label"        => "Life Stage",
        "rewrite"      => ["slug" => "results/life-stage"],
        "public"       => true,
        "hierarchical" => false,
        "show_in_rest" => true,
    ]);
}
