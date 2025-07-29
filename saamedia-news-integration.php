<?php
/*
Plugin Name: SaaMedia News Integration
Description: Receives API webhook from external news automation system.
Version: 1.0
*/

add_action('rest_api_init', function () {
    register_rest_route('saamedia/v1', '/post-news', array(
        'methods' => 'POST',
        'callback' => 'saamedia_receive_news',
        'permission_callback' => '__return_true',
    ));
});

function saamedia_receive_news($data) {
    $params = $data->get_json_params();

    $title = sanitize_text_field($params['title']);
    $content = wp_kses_post($params['content']);
    $category = sanitize_text_field($params['category']);

    $post = array(
        'post_title'    => $title,
        'post_content'  => $content,
        'post_status'   => 'publish',
        'post_author'   => 1,
        'tags_input'    => array($category),
    );

    $post_id = wp_insert_post($post);

    if ($post_id) {
        return new WP_REST_Response(['status' => 'success', 'id' => $post_id], 200);
    } else {
        return new WP_REST_Response(['status' => 'error'], 500);
    }
}
?>
