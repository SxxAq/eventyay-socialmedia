all: localecompile
LNGS:=$(shell python3 -c 'import os; print(" ".join(f"-l {d}" for d in os.listdir("socialmedia/locale") if os.path.isdir(os.path.join("socialmedia/locale", d)))) if os.path.exists("socialmedia/locale") else print("")')

localecompile:
	django-admin compilemessages

localegen:
	django-admin makemessages --keep-pot -i build -i dist -i "*egg*" $(LNGS)

.PHONY: all localecompile localegen
