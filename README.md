# power_system
- Submodule for basic power system functionality.

- To initialize the submodule in the project use

``` sh
git submodule add https://github.com/KemalParlaktuna/power_system.git
git add .gitmodules power_system
git commit -m "Added power_system as a submodule"
git push origin main
```

- To update the submodule commit in project to the latest version use 

```sh  
git submodule update --remote --merge
git add power_system
git commit -m "Updated power_system submodule reference to latest commit"
git push origin main
```

- To clone a project with submodules use

```sh
git clone --recurse-submodules <submodule_url>
```
