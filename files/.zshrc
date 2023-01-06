# setopt autocd
# bindkey -e

# zstyle :compinstall filename "$HOME/.zshrc"
autoload -U compinit
compinit

for file in $HOME/.zsh/* ; do
	[[ -r "$file" ]] && . "$file"
done
unset file