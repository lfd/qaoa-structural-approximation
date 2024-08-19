let SessionLoad = 1
let s:so_save = &g:so | let s:siso_save = &g:siso | setg so=0 siso=0 | setl so=-1 siso=-1
let v:this_session=expand("<sfile>:p")
silent only
silent tabonly
cd ~/Documents/phd/qaoa_layer_amplitudes/cost_function_expectation_paper_data/sim
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
let s:shortmess_save = &shortmess
if &shortmess =~ 'A'
  set shortmess=aoOA
else
  set shortmess=aoO
endif
badd +1 sim.py
badd +22 train_on_QPU.py
badd +61 train_on_CPU.py
argglobal
%argdel
$argadd sim.py
edit sim.py
let s:save_splitbelow = &splitbelow
let s:save_splitright = &splitright
set splitbelow splitright
wincmd _ | wincmd |
split
1wincmd k
wincmd w
wincmd _ | wincmd |
vsplit
1wincmd h
wincmd w
let &splitbelow = s:save_splitbelow
let &splitright = s:save_splitright
wincmd t
let s:save_winminheight = &winminheight
let s:save_winminwidth = &winminwidth
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
exe '1resize ' . ((&lines * 57 + 58) / 116)
exe '2resize ' . ((&lines * 56 + 58) / 116)
exe 'vert 2resize ' . ((&columns * 103 + 106) / 212)
exe '3resize ' . ((&lines * 56 + 58) / 116)
exe 'vert 3resize ' . ((&columns * 108 + 106) / 212)
argglobal
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let &fdl = &fdl
let s:l = 51 - ((50 * winheight(0) + 28) / 57)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 51
normal! 018|
wincmd w
argglobal
if bufexists(fnamemodify("train_on_QPU.py", ":p")) | buffer train_on_QPU.py | else | edit train_on_QPU.py | endif
if &buftype ==# 'terminal'
  silent file train_on_QPU.py
endif
balt sim.py
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let &fdl = &fdl
let s:l = 16 - ((15 * winheight(0) + 28) / 56)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 16
normal! 0
lcd ~/Documents/phd/qaoa_layer_amplitudes/cost_function_expectation_paper_data/sim
wincmd w
argglobal
if bufexists(fnamemodify("~/Documents/phd/qaoa_layer_amplitudes/cost_function_expectation_paper_data/sim/train_on_CPU.py", ":p")) | buffer ~/Documents/phd/qaoa_layer_amplitudes/cost_function_expectation_paper_data/sim/train_on_CPU.py | else | edit ~/Documents/phd/qaoa_layer_amplitudes/cost_function_expectation_paper_data/sim/train_on_CPU.py | endif
if &buftype ==# 'terminal'
  silent file ~/Documents/phd/qaoa_layer_amplitudes/cost_function_expectation_paper_data/sim/train_on_CPU.py
endif
balt ~/Documents/phd/qaoa_layer_amplitudes/cost_function_expectation_paper_data/sim/sim.py
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let &fdl = &fdl
let s:l = 58 - ((47 * winheight(0) + 28) / 56)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 58
normal! 0
lcd ~/Documents/phd/qaoa_layer_amplitudes/cost_function_expectation_paper_data/sim
wincmd w
exe '1resize ' . ((&lines * 57 + 58) / 116)
exe '2resize ' . ((&lines * 56 + 58) / 116)
exe 'vert 2resize ' . ((&columns * 103 + 106) / 212)
exe '3resize ' . ((&lines * 56 + 58) / 116)
exe 'vert 3resize ' . ((&columns * 108 + 106) / 212)
tabnext 1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0 && getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20
let &shortmess = s:shortmess_save
let &winminheight = s:save_winminheight
let &winminwidth = s:save_winminwidth
let s:sx = expand("<sfile>:p:r")."x.vim"
if filereadable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &g:so = s:so_save | let &g:siso = s:siso_save
nohlsearch
let g:this_session = v:this_session
let g:this_obsession = v:this_session
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
