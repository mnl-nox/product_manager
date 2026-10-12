CC ?= cc
CFLAGS ?= -std=c23 -Wall -Wextra -Wpedantic -Werror -Iinclude
LDFLAGS ?=
TARGET := build/login_term
SOURCES := $(wildcard src/*.c)
OBJECTS := $(patsubst src/%.c,obj/%.o,$(SOURCES))

.PHONY: all run clean

all: $(TARGET)

$(TARGET): $(OBJECTS) | build
	$(CC) $(LDFLAGS) $^ -o $@

obj/%.o: src/%.c | obj
	$(CC) $(CFLAGS) -c $< -o $@

build obj:
	mkdir -p $@

run: $(TARGET)
	./$(TARGET)

clean:
	rm -f obj/*.o $(TARGET)
