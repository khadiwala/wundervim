# wundervim

This implements basic task editing functionality for [WunderList](http://wunderlist.com) as a vim plugin. Primarily focused on features I use - if you would like to see something implemented to support your workflow, feel free to file an issue.
This plugin is highly unstable, please don't let it near any critical data

## Installation

Use your plugin manager of choice.

- [Pathogen](https://github.com/tpope/vim-pathogen)
  - `git clone https://github.com/khadiwala/wundervim ~/.vim/bundle/wundervim`
- [Vundle](https://github.com/gmarik/vundle)
  - Add `Bundle 'https://github.com/khadiwala/wundervim'` to .vimrc
  - Run `:BundleInstall`
- [NeoBundle](https://github.com/Shougo/neobundle.vim)
  - Add `NeoBundle 'https://github.com/khadiwala/wundervim'` to .vimrc
  - Run `:NeoBundleInstall`
- [vim-plug](https://github.com/junegunn/vim-plug)
  - Add `Plug 'https://github.com/khadiwala/wundervim'` to .vimrc
  - Run `:PlugInstall`

Primarily, the commands you can use to interact with Wunderlist are

- :WunderView, which shows your lists and folders
- :WunderTaskUpdate, which will send your local changes to Wunderlist

You can set mappings for these in your vimrc, for example:

```
  " Toggle wunderlist pane
  map <leader>w :WunderView<CR>
  " Persist task updates to WunderList
  map <leader>u :WunderTaskUpdate<CR>
```

Remember, added or completed tasks will not be saved until the :WunderTaskUpdate command is called

## Status

### Working
- View folders / lists
- View uncompleted tasks for a list
- Add a task
- Complete a task
- Subtasks

### Planned
- Reordering of tasks

### Maybe
- Due dates / reminders
- Notes
- Comments
- Creating lists / folders
- Rename a task
