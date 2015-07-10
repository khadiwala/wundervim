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

## Status

### Working
- View folders / lists
- View uncompleted tasks for a list
- Add a task
- Complete a task

### Planned
- Reordering of tasks
- Subtasks

### Maybe
- Due dates / reminders
- Notes
- Comments
- Creating lists / folders
- Rename a task
