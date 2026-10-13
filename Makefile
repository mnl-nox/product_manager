CC ?= cc
CFLAGS ?= -std=c2x -Wall -Wextra -Wpedantic -Werror -Iinclude
LDFLAGS ?=
TARGET := build/product_manager
SOURCES := $(wildcard src/*.c)
OBJECTS := $(patsubst src/%.c,obj/%.o,$(SOURCES))

.PHONY: all run run-api run-desktop test package-linux package-pwa clean

all: $(TARGET)

$(TARGET): $(OBJECTS) | build
	$(CC) $(LDFLAGS) $^ -o $@

obj/%.o: src/%.c | obj
	$(CC) $(CFLAGS) -c $< -o $@

build obj:
	mkdir -p $@

run: $(TARGET)
	./$(TARGET)

run-api:
	python3 api/app.py

run-desktop:
	python3 desktop.py

package-linux:
	bash packaging/linux/build-packages.sh

package-pwa:
	bash packaging/android/build-pwa.sh

test:
	python3 -m unittest discover -s tests -v

clean:
	rm -f obj/*.o $(TARGET)
