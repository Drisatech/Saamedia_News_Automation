<?php
/*
Plugin Name: SaaMedia News Integration
Description: Receives and posts news articles from Python backend.
Version: 1.1
*/

add_action('rest_api_init', function () {
    register_rest_route('saamedia/v1', '/post-news', array(
        'methods' => 'POST',
        'callback' => 'saamedia_receive_news',
        'permission_callback' => '__return_true'
    ));
});

function saamedia_receive_news($request) {
    $params = $request->get_json_params();

    $title = sanitize_text_field($params['title']);
    $content = wp_kses_post($params['content']);
    $category = sanitize_text_field($params['category']);
    $image_url = esc_url_raw($params['image_url']);

    require_once(ABSPATH . 'wp-admin/includes/image.php');
    require_once(ABSPATH . 'wp-admin/includes/file.php');
    require_once(ABSPATH . 'wp-admin/includes/media.php');

    $post = array(
        'post_title'   => $title,
        'post_content' => $content,
        'post_status'  => 'publish',
        'post_author'  => 1,
        'tags_input'   => array($category),
    );

    $post_id = wp_insert_post($post);

    if (!is_wp_error($post_id) && $image_url) {
        $image_id = media_sideload_image($image_url, $post_id, null, 'id');
        if (!is_wp_error($image_id)) {
            set_post_thumbnail($post_id, $image_id);
        }
    }

    return rest_ensure_response(array(
        'success' => true,
        'id' => $post_id,
        'title' => $title,
    ));
}
?>