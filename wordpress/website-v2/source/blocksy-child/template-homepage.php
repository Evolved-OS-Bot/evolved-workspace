<?php
/**
 * Template Name: Homepage (Full Width)
 */
?><!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo('charset'); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<?php wp_head(); ?>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #0a0a0a; color: #f5f0eb; font-family: "Lato", sans-serif; }
</style>
</head>
<body <?php body_class('evolved-homepage'); ?>>
<?php wp_body_open(); ?>
<main>
<?php
while (have_posts()) {
    the_post();
    // Output raw stored HTML — bypass wpautop and all content filters
    echo get_post_field('post_content', get_the_ID());
}
?>
</main>
<?php wp_footer(); ?>
</body>
</html>
