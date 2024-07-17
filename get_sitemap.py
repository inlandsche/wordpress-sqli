from usp.tree import sitemap_tree_for_homepage

tree = sitemap_tree_for_homepage('https://filkom.ub.ac.id/')
# all_pages() returns an Iterator

with open('sitemap-url', 'w') as f:
    for page in tree.all_pages():
        f.write(page.url)
        f.write('\n')

