#[component]
pub fn SearchView() -> Element {
    let is_online = use_network_condition();
    let search = use_search_state();
    if !is_online() { return rsx! { SearchDisabledRendition {} }; }
    match search() { None => rsx! { SearchLoadingRendition {} }, Some(Ok(_)) => rsx! {} }
}
