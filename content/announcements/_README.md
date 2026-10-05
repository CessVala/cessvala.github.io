# Adding an announcement

Copy `_example.md` to a file named `YYYY-MM-DD-short-title.md`. Replace the
example date, titles, summaries, optional paper details, and the English and
Chinese text. The summary appears on Home and in the announcement archive;
the text beneath each language heading appears on its article page.

After the site is moved to your GitHub Pages repository, you can create or
edit the announcement file in GitHub's web editor and commit it to the default
branch. GitHub will build and publish the English and Chinese pages and both
news lists automatically. You will not need to use Python or contact anyone.

To generate the pages locally, run this command from the project folder:

```sh
python build_announcements.py
```

The command creates matching English and Chinese announcement pages and
updates the latest news and full archive in both languages. It leaves existing
announcement pages in place. When the finished site moves to GitHub Pages,
this command can be run in a GitHub Actions publishing workflow, or the
announcement sources can be migrated to native Jekyll posts.

The local build needs Python, PyYAML, and lxml. If those packages are missing, run
`python -m pip install PyYAML lxml`. Running the command generates files locally;
it does not publish the website.
