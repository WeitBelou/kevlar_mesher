.PHONY: build
build:
	gcc -c -Wall -Werror -fpic solver.c
	gcc -shared -o libsolver.so solver.o

.PHONY: install
install: build
	cp libsolver.so /usr/lib/libsolver.so
