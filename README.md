# power_system
- Submodule for basic power system functionality.

- To initialize the submodule in the project use

``` sh
git submodule add <submodule_url>
git add .gitmodules <submodule_name>
git commit -m "Added <submodule_name> as a submodule"
git push origin main
```

- To update the submodule commit in project to the latest version use 

```sh  
git submodule update --remote --merge
```

- To clone a project with submodules use

```sh
git clone --recurse-submodules <submodule_url>
