CC ?= cc
CFLAGS ?= -std=c23 -Wall -Wextra -Wpedantic -Werror -Iinclude
LDFLAGS ?=
TARGET := build/product_manager
SOURCES := $(wildcard src/*.c)
OBJECTS := $(patsubst src/%.c,obj/%.o,$(SOURCES))

.PHONY: all run run-api test clean

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

test:
	python3 -m unittest discover -s tests -v

clean:
	rm -f obj/*.o $(TARGET)
