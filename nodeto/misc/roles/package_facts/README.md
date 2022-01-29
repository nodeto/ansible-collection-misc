# Package Facts
Helps speed up playbooks by caching the list of available package the first
time it is called and then invoking ansible.builtin.apt only if the package is
not already installed.

To use, first specify nodeto.misc.package_facts as a dependency to your role.
This will load the package list.

Then to install a package use the following format:
```
- name: NIX IS INSTALLED FOR ALL USERS
  ansible.builtin.include_role:
    name: nodeto.misc.package_facts
    tasks_from: packages.yml
  vars:
    package_facts_needed:
      - restic
```
