# setopt autocd
setopt prompt_subst
# bindkey -e

# zstyle :compinstall filename "$HOME/.zshrc"
autoload -U compinit
compinit

autoload -U colors
colors # Enable colors in prompt

for file in $HOME/.zsh/* ; do
	[[ -r "$file" ]] && . "$file"
done
unset file

# PATH
#test -d $HOME/.local/bin && PATH=$PATH:$HOME/.local/bin