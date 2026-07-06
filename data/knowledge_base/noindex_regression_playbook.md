# Noindex Regression Playbook

Business objective: prevent accidental indexability changes from turning into traffic loss.

If a revenue-critical page has `noindex` in the meta robots tag, treat this as an urgent technical regression. The first fix is not content; it is removing the noindex directive, validating the deployed template, requesting reindexing, and adding a deployment gate to prevent recurrence.

Evidence signals:
- meta robots contains noindex
- robots.txt blocks the URL
- canonical points to a different page without intent to consolidate
- status code is not 200

Recommended actions:
- remove noindex immediately
- validate template and CMS release history
- request reindexing
- add automated indexability checks after deployment
- notify SEO and engineering owners
