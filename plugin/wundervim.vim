" --------------------------------
" Add our plugin to the path
" --------------------------------

python << endOfPython
import sys
import vim
sys.path.append(vim.eval('expand("<sfile>:h")'))
from api import get_client
endOfPython

" --------------------------------
"  Function(s)
" --------------------------------


function! WunderView()
30vnew
set buftype=nofile
noremap <buffer> <CR> :WunderTaskViewPrevWindow<CR>
noremap <buffer> o :WunderTaskViewPrevWindow<CR>
noremap <buffer> t :WunderTaskViewNewTab<CR>
noremap <buffer> T :WunderTaskViewNewTabSilent<CR>
noremap <buffer> i :WunderTaskViewSplit<CR>
noremap <buffer> s :WunderTaskViewSplitVertical<CR>
python << endOfPython

from wundervim import wunder_view
vim.current.buffer[:] = wunder_view(get_client())

endOfPython
endfunction


function! UpdateTasks()
python << endOfPython

from wundervim import update_tasks
update_tasks(get_client(), vim.current.buffer[:])

endOfPython
endfunction

function! TaskView(line)
python << endOfPython

set buftype=nofile
from wundervim import task_view
line = vim.eval("a:line")
vim.current.buffer[:] = task_view(get_client(), line)

endOfPython
endfunction



" --------------------------------
"  Task opening configs
" --------------------------------

function! TaskViewPrevWindow()
    let myline=getline('.')
    wincmd p
    enew
    call TaskView(myline)
endfunction

function! TaskViewCurrentWindow()
    let myline=getline('.')
    enew
    call TaskView(myline)
endfunction

function! TaskViewSplit()
    let myline=getline('.')
    new
    call TaskView(myline)
endfunction

function! TaskViewSplitVertical()
    let myline=getline('.')
    vnew
    call TaskView(myline)
endfunction

function! TaskViewNewTab()
    let myline=getline('.')
    tabnew
    call TaskView(myline)
endfunction

function! TaskViewNewTabSilent()
    let myline=getline('.')
    tabnew
    tabp
    call TaskView(myline)
endfunction


" --------------------------------
"  Expose our commands to the user
" --------------------------------
command! WunderView call WunderView()
command! WunderTaskView call TaskView()
command! WunderTaskViewPrevWindow call TaskViewPrevWindow()
command! WunderTaskViewCurrentWindow call TaskViewCurrentWindow()
command! WunderTaskViewNewTab call TaskViewNewTab()
command! WunderTaskViewNewTabSilent call TaskViewNewTabSilent()
command! WunderTaskViewSplit call TaskViewSplit()
command! WunderTaskViewSplitVertical call TaskViewSplitVertical()
command! WunderTaskUpdate call UpdateTasks()
