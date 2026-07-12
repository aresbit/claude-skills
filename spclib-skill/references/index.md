# sp.h API Reference Index

> Auto-generated from sp.h upstream. Use Ctrl+F to search for specific APIs.
> All public functions are marked with `SP_API`.

## Table of Contents

- [Core Concepts](#core-concepts)
- [Type Aliases](#type-aliases)
- [Core Structs](#core-structs)
- [Constants & Macros](#constants--macros)
- [Memory (sp_mem)](#memory-sp_mem)
- [String (sp_str)](#string-sp_str)
- [C String (sp_cstr)](#c-string-sp_cstr)
- [Dynamic Array (sp_da)](#dynamic-array-sp_da)
- [Hash Table (sp_ht)](#hash-table-sp_ht)
- [IO (sp_io)](#io-sp_io)
- [Filesystem (sp_fs)](#filesystem-sp_fs)
- [Process (sp_ps)](#process-sp_ps)
- [Time (sp_tm)](#time-sp_tm)
- [Threading](#threading)
- [Formatting (sp_fmt)](#formatting-sp_fmt)
- [Logging & Printing](#logging--printing)
- [Parsing (sp_parse)](#parsing-sp_parse)
- [UTF-8 (sp_utf8)](#utf-8-sp_utf8)
- [WTF-8/WTF-16](#wtf-8wtf-16)
- [Environment (sp_env)](#environment-sp_env)
- [Platform (sp_os)](#platform-sp_os)
- [File Monitor (sp_fmon)](#file-monitor-sp_fmon)
- [Application (sp_app)](#application-sp_app)
- [System (sp_sys)](#system-sp_sys)
- [Error Handling](#error-handling)
- [Quick Lookup by Task](#quick-lookup-by-task)
- [Prefix Reference](#prefix-reference)

---

## Core Concepts

### Allocator Model
All allocations in sp.h go through an `sp_mem_t` allocator handle:
```c
sp_mem_t mem = sp_mem_os_new();       // OS-backed allocator
sp_mem_arena_t* arena = sp_mem_arena_new(mem);  // Arena allocator
void* ptr = sp_alloc(mem, 1024);      // Allocate via allocator
sp_free(mem, ptr);                    // Free via allocator
```

### String Model
`sp_str_t` is a {data, len} string view — no null termination required:
```c
sp_str_t s = sp_str_view("hello");   // Zero-allocation view
sp_str_t s2 = sp_str_copy(mem, s);   // Allocated copy
bool eq = sp_str_equal(s, s2);       // Compare
```

### Scratch Space
Use scratch arenas for temporary allocations:
```c
sp_mem_arena_marker_t mark = sp_mem_begin_scratch();
sp_str_t msg = sp_fmt(sp_mem_get_scratch(), "hello {}", SP_FMT_STR(name));
sp_mem_end_scratch(mark);  // All scratch memory freed
```

---

## Type Aliases

```c
typedef int8_t   s8;   typedef uint8_t  u8;
typedef int16_t  s16;  typedef uint16_t u16;
typedef int32_t  s32;  typedef uint32_t u32;
typedef int64_t  s64;  typedef uint64_t u64;
typedef float    f32;  typedef double   f64;
typedef char     c8;   typedef wchar_t  c16;
typedef u64      sp_hash_t;
typedef u64      sp_ht_it_t;
typedef u64      sp_tm_point_t;
typedef s32      sp_atomic_s32_t;
typedef void*    sp_atomic_ptr_t;
typedef s32      sp_spin_lock_t;
```

---

## Core Structs

```c
// String view (ptr + len, no null termination)
typedef struct { const c8* data; u32 len; } sp_str_t;

// Wide string view
typedef struct { const u16* data; u32 len; } sp_wide_str_t;

// Memory allocator handle (opaque)
typedef struct sp_mem_s sp_mem_t;

// Memory slice (byte slice)
typedef struct { u8* data; u64 len; } sp_mem_slice_t;

// IO Writer (vtable-based polymorphic writer)
typedef struct sp_io_writer sp_io_writer_t;

// IO Reader (vtable-based polymorphic reader)
typedef struct sp_io_reader sp_io_reader_t;

// Process output
typedef struct {
  sp_str_t out;
  sp_str_t err;
  s32 exit_code;
} sp_ps_output_t;

// Process status
typedef struct {
  bool exited;
  s32 exit_code;
  bool signaled;
  s32 signal;
} sp_ps_status_t;

// File system entry
typedef struct {
  sp_str_t path;
  sp_str_t name;
  sp_fs_kind_t kind;
} sp_fs_entry_t;

// Date/time epoch
typedef struct {
  u64 s;
  u64 ns;
} sp_tm_epoch_t;

// Date/time components
typedef struct {
  s32 year; s32 month;  s32 day;
  s32 hour; s32 minute; s32 second;
  s32 millisecond; s32 microsecond; s32 nanosecond;
} sp_tm_date_time_t;
```

---

## Constants & Macros

### Null Values
```c
#define SP_NULL     0
#define SP_NULLPTR  ((void*)0)
```

### Initialization
```c
#define SP_ZERO_INITIALIZE()  {0}
#define SP_ZERO_STRUCT(T)     (T){0}
```

### Utility Macros
```c
#define SP_MAX(a, b)          ((a) > (b) ? (a) : (b))
#define SP_MIN(a, b)          ((a) < (b) ? (a) : (b))
#define SP_SWAP(T, a, b)      { T _tmp = (a); (a) = (b); (b) = _tmp; }
#define SP_UNUSED(x)          ((void)(x))
#define SP_CARR_LEN(arr)      (sizeof(arr) / sizeof((arr)[0]))
#define SP_MEM_ALIGNMENT      16
```

### Loop Macros
```c
#define sp_for(it, n)              for (u32 it = 0; it < (n); it++)
#define sp_for_range(it, lo, hi)   for (u32 it = (lo); it < (hi); it++)
#define sp_carr_for(arr, it)       for (u32 it = 0; it < SP_CARR_LEN(arr); it++)
```

---

## Memory (sp_mem)

sp.h uses an explicit allocator model. Every allocation requires an `sp_mem_t` handle.

### Core Allocation
```c
SP_API void                  sp_mem_copy(void* dest, const void* source, u64 num_bytes);
SP_API void                  sp_mem_move(void* dest, const void* source, u64 num_bytes);
SP_API bool                  sp_mem_is_equal(const void* a, const void* b, u64 len);
SP_API void                  sp_mem_fill(void* buffer, u64 bsize, void* fill, u64 fsize);
SP_API void                  sp_mem_fill_u8(void* buffer, u64 buffer_size, u8 fill);
SP_API void                  sp_mem_zero(void* buffer, u64 buffer_size);
```

### OS Allocator
```c
SP_API void*                 sp_mem_os_alloc(u64 size);
SP_API void*                 sp_mem_os_alloc_zero(u64 size);
SP_API void*                 sp_mem_os_realloc(void* ptr, u64 size);
SP_API void                  sp_mem_os_free(void* ptr);
SP_API void*                 sp_mem_os_on_alloc(void* ud, sp_mem_alloc_mode_t mode, u64 size, void* ptr);
SP_API sp_mem_os_header_t*   sp_mem_os_get_header(void* ptr);
SP_API sp_mem_t              sp_mem_os_new();
```

### Arena Allocator
```c
SP_API sp_mem_t              sp_mem_arena_as_allocator(sp_mem_arena_t* arena);
SP_API sp_mem_arena_t*       sp_mem_arena_new(sp_mem_t mem);
SP_API sp_mem_arena_t*       sp_mem_arena_new_ex(sp_mem_t mem, u64 block_size, sp_mem_arena_mode_t mode, u8 alignment);
SP_API void                  sp_mem_arena_clear(sp_mem_arena_t* arena);
SP_API void                  sp_mem_arena_destroy(sp_mem_arena_t* arena);
SP_API void*                 sp_mem_arena_on_alloc(void* ptr, sp_mem_alloc_mode_t mode, u64 n, void* old);
SP_API sp_mem_arena_marker_t sp_mem_arena_mark(sp_mem_arena_t* a);
SP_API void                  sp_mem_arena_pop(sp_mem_arena_marker_t marker);
SP_API u64                   sp_mem_arena_capacity(sp_mem_arena_t* arena);
SP_API u64                   sp_mem_arena_bytes_used(sp_mem_arena_t* arena);
SP_API void*                 sp_mem_arena_alloc(sp_mem_arena_t* arena, u64 size);
SP_API void*                 sp_mem_arena_realloc(sp_mem_arena_t* arena, void* ptr, u64 size);
SP_API void                  sp_mem_arena_free(sp_mem_arena_t* arena, void* ptr);
```

### Fixed Buffer Allocator
```c
SP_API sp_mem_fixed_t        sp_mem_fixed_ex(void* buffer, u64 capacity, u8 alignment);
SP_API sp_mem_t              sp_mem_fixed_as_allocator(sp_mem_fixed_t* fixed);
SP_API void                  sp_mem_fixed_clear(sp_mem_fixed_t* fixed);
SP_API u64                   sp_mem_fixed_bytes_used(sp_mem_fixed_t* fixed);
SP_API void*                 sp_mem_fixed_on_alloc(void* ud, sp_mem_alloc_mode_t mode, u64 size, void* old);
```

### Scratch Space
```c
SP_API sp_mem_t              sp_mem_get_scratch();
SP_API sp_mem_arena_t*       sp_mem_get_scratch_arena();
SP_API sp_mem_arena_t*       sp_mem_get_scratch_arena_for(sp_mem_t mem);
SP_API sp_mem_arena_marker_t sp_mem_begin_scratch();
SP_API sp_mem_arena_marker_t sp_mem_begin_scratch_for(sp_mem_t mem);
SP_API void                  sp_mem_end_scratch(sp_mem_arena_marker_t marker);
```

### Memory Slice
```c
SP_API sp_mem_slice_t    sp_mem_slice_sub(sp_mem_slice_t slice, u64 start, u64 len);
SP_API sp_mem_slice_t    sp_mem_slice_prefix(sp_mem_slice_t slice, u64 len);
SP_API sp_mem_slice_t    sp_mem_slice_suffix(sp_mem_slice_t slice, u64 len);
SP_API bool              sp_mem_slice_empty(sp_mem_slice_t slice);
SP_API u8                sp_mem_slice_at(sp_mem_slice_t slice, u64 index);
SP_API sp_mem_slice_it_t sp_mem_slice_it(sp_mem_slice_t slice);
SP_API bool              sp_mem_slice_it_valid(sp_mem_slice_it_t* it);
SP_API void              sp_mem_slice_it_next(sp_mem_slice_it_t* it);
SP_API sp_mem_buffer_as_str(sp_mem_buffer_t* buffer);
SP_API c8* sp_mem_buffer_as_cstr(sp_mem_buffer_t* buffer);
```

### Enums
```c
typedef enum { ... } sp_mem_alloc_mode_t;
typedef enum { ... } sp_mem_arena_mode_t;
```

---

## String (sp_str)

### Creation
```c
SP_API sp_str_t        sp_str(const c8* str, u32 len);
SP_API c8*             sp_str_to_cstr(sp_mem_t mem, sp_str_t str);
SP_API sp_str_t        sp_str_copy(sp_mem_t mem, sp_str_t str);
SP_API sp_str_t        sp_str_from_cstr(sp_mem_t mem, const c8* str);
SP_API sp_str_t        sp_str_from_cstr_n(sp_mem_t mem, const c8* str, u32 len);
SP_API sp_str_t        sp_str_alloc(sp_mem_t mem, u32 capacity);
SP_API sp_str_t        sp_str_view(const c8* cstr);
```

### Query
```c
SP_API bool            sp_str_empty(sp_str_t);
SP_API bool            sp_str_equal(sp_str_t a, sp_str_t b);
SP_API bool            sp_str_equal_cstr(sp_str_t a, const c8* b);
SP_API bool            sp_str_starts_with(sp_str_t str, sp_str_t prefix);
SP_API bool            sp_str_ends_with(sp_str_t str, sp_str_t suffix);
SP_API bool            sp_str_contains(sp_str_t str, sp_str_t needle);
SP_API s32             sp_str_find(sp_str_t str, sp_str_t needle);
SP_API s32             sp_str_find_c8(sp_str_t str, c8 needle);
SP_API s32             sp_str_find_c8_reverse(sp_str_t str, c8 needle);
SP_API bool            sp_str_valid(sp_str_t str);
SP_API c8              sp_str_at(sp_str_t str, s32 index);
SP_API c8              sp_str_at_reverse(sp_str_t str, s32 index);
SP_API c8              sp_str_back(sp_str_t str);
SP_API s32             sp_str_compare_alphabetical(sp_str_t a, sp_str_t b);
```

### Slicing
```c
SP_API sp_str_t        sp_str_prefix(sp_str_t str, s32 len);
SP_API sp_str_t        sp_str_suffix(sp_str_t str, s32 len);
SP_API sp_str_t        sp_str_sub(sp_str_t str, s32 index, s32 len);
SP_API sp_str_t        sp_str_sub_reverse(sp_str_t str, s32 index, s32 len);
SP_API sp_str_pair_t   sp_str_cleave_c8(sp_str_t str, c8 delimiter);
```

### Manipulation (allocates via sp_mem_t)
```c
SP_API sp_str_t        sp_str_concat(sp_mem_t mem, sp_str_t a, sp_str_t b);
SP_API sp_str_t        sp_str_join(sp_mem_t mem, sp_str_t a, sp_str_t b, sp_str_t join);
SP_API sp_str_t        sp_str_join_n(sp_mem_t mem, sp_str_t* strs, u32 n, sp_str_t joiner);
SP_API sp_str_t        sp_str_replace_c8(sp_mem_t mem, sp_str_t str, c8 from, c8 to);
SP_API sp_str_t        sp_str_pad(sp_mem_t mem, sp_str_t str, u32 n);
SP_API sp_str_t        sp_str_trim_left(sp_str_t str);
SP_API sp_str_t        sp_str_trim_right(sp_str_t str);
SP_API sp_str_t        sp_str_trim(sp_str_t str);
SP_API sp_str_t        sp_str_strip_left(sp_str_t str, sp_str_t strip);
SP_API sp_str_t        sp_str_strip_right(sp_str_t str, sp_str_t strip);
SP_API sp_str_t        sp_str_strip(sp_str_t str, sp_str_t strip);
SP_API sp_str_t        sp_str_truncate(sp_mem_t mem, sp_str_t str, u32 n, sp_str_t trailer);
SP_API sp_str_t        sp_str_join_cstr_n(sp_mem_t mem, const c8** strings, u32 num_strings, sp_str_t join);
SP_API sp_str_t        sp_str_to_upper(sp_mem_t mem, sp_str_t str);
SP_API sp_str_t        sp_str_to_lower(sp_mem_t mem, sp_str_t str);
SP_API sp_str_t        sp_str_to_pascal_case(sp_mem_t mem, sp_str_t str);
```

### Map / Reduce
```c
SP_API sp_str_t        sp_str_reduce(sp_mem_t mem, sp_str_t* strs, u32 n, void* ud, sp_str_reduce_fn_t fn);
SP_API void            sp_str_reduce_kernel_join(sp_str_reduce_context_t* context);
SP_API sp_str_t        sp_str_map_kernel_prepend(sp_str_map_context_t* context);
SP_API sp_str_t        sp_str_map_kernel_append(sp_str_map_context_t* context);
SP_API sp_str_t        sp_str_map_kernel_prefix(sp_str_map_context_t* context);
SP_API sp_str_t        sp_str_map_kernel_trim(sp_str_map_context_t* context);
SP_API sp_str_t        sp_str_map_kernel_pad(sp_str_map_context_t* context);
SP_API sp_str_t        sp_str_map_kernel_to_upper(sp_str_map_context_t* context);
SP_API sp_str_t        sp_str_map_kernel_to_lower(sp_str_map_context_t* context);
SP_API sp_str_t        sp_str_map_kernel_pascal_case(sp_str_map_context_t* context);
SP_API s32             sp_str_sort_kernel_alphabetical(const void* a, const void* b);
```

---

## C String (sp_cstr)
```c
SP_API c8*             sp_cstr_from_str(sp_mem_t mem, sp_str_t str);
SP_API c8*             sp_cstr_copy(sp_mem_t mem, const c8* cstr);
SP_API c8*             sp_cstr_copy_n(sp_mem_t mem, const c8* str, u32 len);
SP_API void            sp_cstr_copy_to(const c8* str, c8* buffer, u32 buffer_len);
SP_API void            sp_cstr_copy_to_n(const c8* str, u32 len, c8* buffer, u32 buffer_len);
SP_API bool            sp_cstr_equal(const c8* a, const c8* b);
SP_API u32             sp_cstr_len(const c8* str);
SP_API u32             sp_cstr_len_n(const c8* str, u32 n);
SP_API sp_str_t        sp_cstr_as_str(const c8* str);
```

---

## Dynamic Array (sp_da)

### Type Declaration
```c
sp_da(T) name;    // Dynamic array of type T
```

### Core Operations
```c
SP_API void* sp_da_init_ex(sp_mem_t mem, u32 stride);
SP_API void* sp_da_resize(void* arr, u32 stride, u64 len);
SP_API void* sp_da_grow_ex(void* arr, u32 stride, u64 addlen);
SP_API void  sp_da_push_ex(void** arr, void* val, u32 stride);
SP_API sp_da(sp_str_t) sp_str_split_c8(sp_mem_t mem, sp_str_t str, c8 c);
SP_API sp_da(sp_str_t) sp_str_pad_to_longest(sp_mem_t mem, sp_str_t* strs, u32 n);
SP_API sp_da(sp_str_t) sp_str_map(sp_mem_t mem, sp_str_t* s, u32 n, void* ud, sp_str_map_fn_t fn);
SP_API sp_da(sp_fs_entry_t) sp_fs_collect(sp_mem_t mem, sp_str_t path);
SP_API sp_da(sp_fs_entry_t) sp_fs_collect_recursive(sp_mem_t mem, sp_str_t path);
```

### Macro Operations
```c
#define sp_da_init(mem, T)           sp_da_init_ex(mem, sizeof(T))
#define sp_da_push(arr, val)         sp_da_push_ex((void**)&(arr), &(val), sizeof((arr)[0]))
#define sp_da_size(arr)              ...
#define sp_da_capacity(arr)          ...
#define sp_da_free(arr)              ...
#define sp_da_clear(arr)             ...
#define sp_da_back(arr)              ...
#define sp_da_resize(arr, n)         ...
#define sp_da_grow(arr, n)           ...
```

---

## Hash Table (sp_ht)

sp_ht uses macro-based generic hash tables. See sp.h source for full macro definitions.

### Type Declaration
```c
sp_ht(key_type, value_type) name;
```

### Built-in Hash/Compare Functions
```c
SP_API u64         sp_ht_get_key_index_fn(void** data, void* key, u64 capacity, sp_ht_info_t info);
SP_API void        sp_ht_resize_impl(void** data, u64 old_cap, u64 new_cap, sp_ht_info_t info);
SP_API void        sp_ht_insert_impl(void* ht, void* key, void* val, sp_ht_info_t info);
SP_API sp_ht_it_t  sp_ht_it_init_fn(void** data, u64 capacity, sp_ht_info_t info);
SP_API void        sp_ht_it_advance_fn(void** data, u64 capacity, u64* it, sp_ht_info_t info);
SP_API sp_hash_t   sp_ht_on_hash_key(void* key, u64 size);
SP_API bool        sp_ht_on_compare_key(void* ka, void* kb, u64 size);
SP_API sp_hash_t   sp_ht_on_hash_str_key(void* key, u64 size);
SP_API bool        sp_ht_on_compare_str_key(void* ka, void* kb, u64 size);
SP_API sp_hash_t   sp_ht_on_hash_cstr_key(void* key, u64 size);
SP_API bool        sp_ht_on_compare_cstr_key(void* ka, void* kb, u64 size);
```

### Hash Utilities
```c
SP_API sp_hash_t sp_hash_cstr(const c8* str);
SP_API sp_hash_t sp_hash_combine(sp_hash_t* hashes, u32 num_hashes);
SP_API sp_hash_t sp_hash_bytes(const void* p, u64 len, u64 seed);
```

---

## IO (sp_io)

IO uses vtable-based polymorphic readers and writers.

### Generic IO
```c
SP_API sp_err_t       sp_io_copy(sp_io_writer_t* dst, sp_io_reader_t* src, u64* bytes_copied);
SP_API sp_err_t       sp_io_read(sp_io_reader_t* reader, void* ptr, u64 size, u64* bytes_read);
SP_API sp_err_t       sp_io_read_file(sp_mem_t mem, sp_str_t path, sp_str_t* content);
SP_API sp_err_t       sp_io_write(sp_io_writer_t* writer, const void* ptr, u64 size, u64* bytes_written);
SP_API sp_err_t       sp_io_write_str(sp_io_writer_t* writer, sp_str_t str, u64* bytes_written);
SP_API sp_err_t       sp_io_write_cstr(sp_io_writer_t* writer, const c8* cstr, u64* bytes_written);
SP_API sp_err_t       sp_io_write_c8(sp_io_writer_t* writer, c8 c);
SP_API sp_err_t       sp_io_write_all(sp_io_writer_t* writer, const void* data, u64 size, u64* bytes_written);
SP_API sp_err_t       sp_io_pad(sp_io_writer_t* writer, u64 size, u64* bytes_written);
SP_API sp_err_t       sp_io_flush(sp_io_writer_t* w);
```

### Reader Types
```c
SP_API void           sp_io_reader_from_mem(sp_io_reader_t* reader, const void* ptr, u64 size);
SP_API void           sp_io_reader_set_buffer(sp_io_reader_t* reader, u8* buf, u64 capacity);
```

### Writer Types
```c
SP_API sp_err_t       sp_io_writer_set_buffer(sp_io_writer_t* writer, u8* buf, u64 capacity);
```

### File Reader
```c
SP_API void           sp_io_seeking_reader_from_file_reader(sp_io_seeking_reader_t* sr, sp_io_file_reader_t* fr);
SP_API sp_err_t       sp_io_file_reader_from_path(sp_io_file_reader_t* r, sp_str_t path);
SP_API sp_err_t       sp_io_file_reader_from_file(sp_io_file_reader_t* r, sp_sys_fd_t file, sp_io_close_mode_t mode);
SP_API sp_err_t       sp_io_file_reader_seek(sp_io_file_reader_t* r, s64 offset, sp_io_whence_t whence, s64* position);
SP_API sp_err_t       sp_io_file_reader_size(sp_io_file_reader_t* r, u64* size);
SP_API sp_err_t       sp_io_file_reader_size_force(sp_io_file_reader_t* r, u64* size);
SP_API sp_err_t       sp_io_file_reader_close(sp_io_file_reader_t* r);
```

### File Writer
```c
SP_API sp_err_t       sp_io_file_writer_from_path(sp_io_file_writer_t* w, sp_str_t path);
SP_API sp_err_t       sp_io_file_writer_from_fd(sp_io_file_writer_t* w, sp_sys_fd_t fd, sp_io_close_mode_t close_mode);
SP_API sp_err_t       sp_io_file_writer_seek(sp_io_file_writer_t* w, s64 offset, sp_io_whence_t whence, s64* position);
SP_API sp_err_t       sp_io_file_writer_size(sp_io_file_writer_t* w, u64* size);
SP_API sp_err_t       sp_io_file_writer_size_force(sp_io_file_writer_t* w, u64* size);
SP_API sp_err_t       sp_io_file_writer_close(sp_io_file_writer_t* w);
```

### Stream Reader/Writer (stdin/stdout/stderr)
```c
SP_API void           sp_io_stream_reader_from_fd(sp_io_stream_reader_t* r, sp_sys_fd_t fd, sp_io_close_mode_t mode);
SP_API sp_err_t       sp_io_stream_reader_close(sp_io_stream_reader_t* r);
SP_API void           sp_io_stream_writer_from_fd(sp_io_stream_writer_t* w, sp_sys_fd_t fd, sp_io_close_mode_t mode);
SP_API sp_err_t       sp_io_stream_writer_close(sp_io_stream_writer_t* w);
SP_API void           sp_io_get_std_out(sp_io_stream_writer_t* io);
SP_API void           sp_io_get_std_err(sp_io_stream_writer_t* io);
```

### Memory Writer
```c
SP_API void           sp_io_mem_writer_from_buffer(sp_io_mem_writer_t* w, void* ptr, u64 size);
SP_API sp_err_t       sp_io_mem_writer_seek(sp_io_mem_writer_t* w, s64 offset, sp_io_whence_t whence, s64* position);
SP_API sp_err_t       sp_io_mem_writer_size(sp_io_mem_writer_t* w, u64* size);
SP_API sp_str_t       sp_io_mem_writer_as_str(sp_io_mem_writer_t* w);
SP_API void           sp_io_dyn_mem_writer_init(sp_mem_t mem, sp_io_dyn_mem_writer_t* w);
SP_API sp_err_t       sp_io_dyn_mem_writer_seek(sp_io_dyn_mem_writer_t* w, s64 offset, sp_io_whence_t whence, s64* position);
SP_API sp_err_t       sp_io_dyn_mem_writer_size(sp_io_dyn_mem_writer_t* w, u64* size);
SP_API sp_err_t       sp_io_dyn_mem_writer_close(sp_io_dyn_mem_writer_t* w);
SP_API sp_str_t       sp_io_dyn_mem_writer_as_str(sp_io_dyn_mem_writer_t* w);
SP_API const c8*      sp_io_dyn_mem_writer_as_cstr(sp_io_dyn_mem_writer_t* w);
```

### Seeking Reader
```c
SP_API sp_err_t       sp_io_seeking_reader_seek(sp_io_seeking_reader_t* r, s64 offset, sp_io_whence_t whence, s64* position);
SP_API void           sp_io_seeking_reader_from_reader(sp_io_seeking_reader_t* sr, sp_io_reader_t* r, sp_io_seek_cb seek);
SP_API void           sp_io_seeking_reader_from_mem(sp_io_seeking_reader_t* sr, sp_io_reader_t* backing, const void* ptr, u64 size);
SP_API void           sp_io_seeking_reader_from_file_reader(sp_io_seeking_reader_t* sr, sp_io_file_reader_t* fr);
SP_API sp_err_t       sp_io_file_reader_seek(sp_io_file_reader_t* r, s64 offset, sp_io_whence_t whence, s64* position);
SP_API sp_err_t       sp_io_file_writer_seek(sp_io_file_writer_t* w, s64 offset, sp_io_whence_t whence, s64* position);
SP_API sp_err_t       sp_io_mem_seek(sp_io_reader_t* r, s64 offset, sp_io_whence_t whence, s64* position);
SP_API sp_err_t       sp_io_mem_writer_seek(sp_io_mem_writer_t* w, s64 offset, sp_io_whence_t whence, s64* position);
SP_API sp_err_t       sp_io_dyn_mem_writer_seek(sp_io_dyn_mem_writer_t* w, s64 offset, sp_io_whence_t whence, s64* position);
```

---

## Filesystem (sp_fs)

### Path Operations
```c
SP_API sp_str_t             sp_fs_get_name(sp_str_t path);
SP_API sp_str_t             sp_fs_parent_path(sp_str_t path);
SP_API sp_str_t             sp_fs_trim_path(sp_str_t path);
SP_API sp_str_t             sp_fs_normalize_path(sp_mem_t mem, sp_str_t path);
SP_API sp_str_t             sp_fs_get_ext(sp_str_t path);
SP_API sp_str_t             sp_fs_get_stem(sp_str_t path);
SP_API sp_str_t             sp_fs_join_path(sp_mem_t mem, sp_str_t a, sp_str_t b);
SP_API sp_str_t             sp_fs_replace_ext(sp_mem_t mem, sp_str_t path, sp_str_t ext);
SP_API void                 sp_fs_it_next(sp_fs_it_t* it);
SP_API sp_str_t             sp_fs_canonicalize_path(sp_mem_t mem, sp_str_t path);
SP_API sp_str_t             sp_fs_get_exe_path(sp_mem_t mem);
SP_API sp_str_t             sp_fs_get_storage_path(sp_mem_t mem);
SP_API sp_str_t             sp_fs_get_config_path(sp_mem_t mem);
```

### Path Queries
```c
SP_API bool                 sp_fs_exists(sp_str_t path);
SP_API bool                 sp_fs_is_file(sp_str_t path);
SP_API bool                 sp_fs_is_dir(sp_str_t path);
SP_API bool                 sp_fs_is_symlink(sp_str_t path);
SP_API bool                 sp_fs_is_target_file(sp_str_t path);
SP_API bool                 sp_fs_is_target_dir(sp_str_t path);
SP_API sp_fs_kind_t         sp_fs_get_kind(sp_str_t path);
SP_API sp_fs_kind_t         sp_fs_get_target_kind(sp_str_t path);
SP_API sp_tm_epoch_t        sp_fs_get_mod_time(sp_str_t path);
```

### File/Directory Creation & Removal
```c
SP_API sp_err_t             sp_fs_create_dir(sp_str_t path);
SP_API sp_err_t             sp_fs_create_file(sp_str_t path);
SP_API sp_err_t             sp_fs_create_file_str(sp_str_t path, sp_str_t str);
SP_API sp_err_t             sp_fs_create_file_slice(sp_str_t path, sp_mem_slice_t slice);
SP_API sp_err_t             sp_fs_create_file_cstr(sp_str_t path, const c8* str);
SP_API sp_err_t             sp_fs_remove_dir(sp_str_t path);
SP_API sp_err_t             sp_fs_remove_file(sp_str_t path);
SP_API sp_err_t             sp_fs_create_hard_link(sp_str_t target, sp_str_t link_path);
SP_API sp_err_t             sp_fs_create_sym_link(sp_str_t target, sp_str_t link_path);
```

### Copy & Link
```c
SP_API bool                 sp_fs_is_symlink(sp_str_t path);
SP_API sp_err_t             sp_fs_create_hard_link(sp_str_t target, sp_str_t link_path);
SP_API sp_err_t             sp_fs_create_sym_link(sp_str_t target, sp_str_t link_path);
SP_API sp_err_t             sp_fs_link(sp_str_t from, sp_str_t to, sp_fs_link_kind_t kind);
SP_API sp_err_t             sp_fs_copy(sp_str_t from, sp_str_t to);
SP_API void                 sp_fs_copy_file(sp_str_t from, sp_str_t to);
SP_API void                 sp_fs_copy_dir(sp_str_t from, sp_str_t to);
SP_API void                 sp_fs_copy_glob(sp_str_t from, sp_str_t glob, sp_str_t to);
```

### Directory Iterator
```c
SP_API sp_fs_it_t           sp_fs_it_new(sp_mem_t mem, sp_str_t path);
SP_API sp_fs_it_t           sp_fs_it_new_recursive(sp_mem_t mem, sp_str_t path);
SP_API void                 sp_fs_it_begin(sp_fs_it_t* it, sp_str_t path);
SP_API void                 sp_fs_it_next(sp_fs_it_t* it);
SP_API void                 sp_fs_it_push(sp_fs_it_t* it, sp_str_t path);
SP_API bool                 sp_fs_it_valid(sp_fs_it_t* it);
SP_API void                 sp_fs_it_deinit(sp_fs_it_t* it);
```

### Directory Collection
```c
```

### Special Paths
```c
SP_API sp_str_t             sp_fs_resolve(sp_mem_t mem, sp_sys_fd_t fd);
SP_API sp_str_t             sp_fs_get_cwd(sp_mem_t mem);
SP_API sp_str_t             sp_fs_get_exe_path(sp_mem_t mem);
SP_API sp_str_t             sp_fs_get_storage_path(sp_mem_t mem);
SP_API sp_str_t             sp_fs_get_config_path(sp_mem_t mem);
```

### Enums
```c
typedef enum { ... } sp_fs_kind_t;
typedef enum { ... } sp_fs_link_kind_t;
typedef enum { ... } sp_fs_path_kind_t;
```

---

## Process (sp_ps)
```c
SP_API sp_ps_t         sp_ps_create(sp_mem_t mem, sp_ps_config_t config);
SP_API sp_ps_output_t  sp_ps_run(sp_mem_t mem, sp_ps_config_t config);
SP_API sp_ps_t         sp_ps_create_c(sp_mem_t mem, sp_ps_config_cstr_t config);
SP_API sp_ps_output_t  sp_ps_run_c(sp_mem_t mem, sp_ps_config_cstr_t config);
SP_API sp_ps_config_t  sp_ps_config_copy(sp_mem_t mem, const sp_ps_config_t* src);
SP_API void            sp_ps_config_add_arg(sp_mem_t mem, sp_ps_config_t* config, sp_str_t arg);
SP_API sp_ps_status_t  sp_ps_wait(sp_ps_t* ps);
SP_API sp_ps_status_t  sp_ps_poll(sp_ps_t* ps, u32 timeout_ms);
SP_API sp_ps_output_t  sp_ps_output(sp_ps_t* ps);
SP_API bool            sp_ps_kill(sp_ps_t* ps);
SP_API void            sp_ps_free(sp_ps_t* ps);
SP_API void            sp_ps_output_free(sp_mem_t mem, sp_ps_output_t* output);
SP_API sp_io_stream_writer_t* sp_ps_io_in(sp_ps_t* ps);
SP_API sp_io_reader_t* sp_ps_io_out(sp_ps_t* ps);
SP_API sp_io_reader_t* sp_ps_io_err(sp_ps_t* ps);
```

### Enums
```c
typedef enum { ... } sp_ps_state_t;
typedef enum { ... } sp_ps_io_mode_t;
typedef enum { ... } sp_ps_env_mode_t;
```

---

## Time (sp_tm)
```c
SP_API sp_tm_epoch_t     sp_tm_now_epoch();
SP_API sp_tm_date_time_t sp_tm_epoch_to_date_time(sp_tm_epoch_t time);
SP_API sp_tm_point_t     sp_tm_now_point();
SP_API u64               sp_tm_point_diff(sp_tm_point_t newer, sp_tm_point_t older);
SP_API sp_tm_timer_t     sp_tm_start_timer();
SP_API u64               sp_tm_read_timer(sp_tm_timer_t* timer);
SP_API u64               sp_tm_lap_timer(sp_tm_timer_t* timer);
SP_API void              sp_tm_reset_timer(sp_tm_timer_t* timer);
SP_API sp_tm_date_time_t sp_tm_get_date_time();
SP_API u64               sp_tm_fps_to_ns(u64 fps);
SP_API u64               sp_tm_s_to_ms(u64 s);
SP_API u64               sp_tm_s_to_us(u64 s);
SP_API u64               sp_tm_s_to_ns(u64 s);
SP_API u64               sp_tm_ms_to_s(u64 ms);
SP_API u64               sp_tm_ms_to_us(u64 ms);
SP_API u64               sp_tm_ms_to_ns(u64 ms);
SP_API u64               sp_tm_us_to_s(u64 us);
SP_API u64               sp_tm_us_to_ms(u64 us);
SP_API u64               sp_tm_us_to_ns(u64 us);
SP_API u64               sp_tm_ns_to_s(u64 ns);
SP_API u64               sp_tm_ns_to_ms(u64 ns);
SP_API u64               sp_tm_ns_to_us(u64 ns);
SP_API f64               sp_tm_s_to_ms_f(f64 s);
SP_API f64               sp_tm_s_to_us_f(f64 s);
SP_API f64               sp_tm_s_to_ns_f(f64 s);
SP_API f64               sp_tm_ms_to_s_f(f64 ms);
SP_API f64               sp_tm_ms_to_us_f(f64 ms);
SP_API f64               sp_tm_ms_to_ns_f(f64 ms);
SP_API f64               sp_tm_us_to_s_f(f64 us);
SP_API f64               sp_tm_us_to_ms_f(f64 us);
SP_API f64               sp_tm_us_to_ns_f(f64 us);
SP_API f64               sp_tm_ns_to_s_f(f64 ns);
SP_API f64               sp_tm_ns_to_ms_f(f64 ns);
SP_API f64               sp_tm_ns_to_us_f(f64 ns);
SP_API sp_str_t          sp_tm_epoch_to_iso8601(sp_mem_t mem, sp_tm_epoch_t time);
SP_API void              sp_tm_epoch_to_iso8601_w(sp_io_writer_t* io, sp_tm_epoch_t time);
```

---

## Threading

### Thread (sp_thread)
```c
SP_API void sp_thread_init(sp_thread_t* thread, sp_thread_fn_t fn, void* userdata);
SP_API void sp_thread_join(sp_thread_t* thread);
SP_API s32  sp_thread_launch(void* userdata);
```

### Mutex (sp_mutex)
```c
SP_API void sp_mutex_init(sp_mutex_t* mutex, sp_mutex_kind_t kind);
SP_API void sp_mutex_lock(sp_mutex_t* mutex);
SP_API void sp_mutex_unlock(sp_mutex_t* mutex);
SP_API void sp_mutex_destroy(sp_mutex_t* mutex);
SP_API s32  sp_mutex_kind_to_c11(sp_mutex_kind_t kind);
```

### Condition Variable (sp_cv)
```c
SP_API void sp_cv_init(sp_cv_t* cv);
SP_API void sp_cv_destroy(sp_cv_t* cv);
SP_API void sp_cv_wait(sp_cv_t* cv, sp_mutex_t* mutex);
SP_API bool sp_cv_wait_for(sp_cv_t* cv, sp_mutex_t* mutex, u32 ms);
SP_API void sp_cv_notify_one(sp_cv_t* cv);
SP_API void sp_cv_notify_all(sp_cv_t* cv);
```

### Semaphore (sp_semaphore)
```c
SP_API void sp_semaphore_init(sp_semaphore_t* semaphore);
SP_API void sp_semaphore_destroy(sp_semaphore_t* semaphore);
SP_API void sp_semaphore_wait(sp_semaphore_t* semaphore);
SP_API bool sp_semaphore_wait_for(sp_semaphore_t* semaphore, u32 ms);
SP_API void sp_semaphore_signal(sp_semaphore_t* semaphore);
```

### Spin Lock (sp_spin)
```c
SP_API void sp_spin_pause();
SP_API bool sp_spin_try_lock(sp_spin_lock_t* lock);
SP_API void sp_spin_lock(sp_spin_lock_t* lock);
SP_API void sp_spin_unlock(sp_spin_lock_t* lock);
```

### Atomics (sp_atomic)
```c
SP_API bool  sp_atomic_s32_cas(sp_atomic_s32_t* value, s32 current, s32 desired);
SP_API s32   sp_atomic_s32_set(sp_atomic_s32_t* value, s32 desired);
SP_API s32   sp_atomic_s32_add(sp_atomic_s32_t* value, s32 add);
SP_API s32   sp_atomic_s32_get(sp_atomic_s32_t* value);
SP_API bool  sp_atomic_ptr_cas(sp_atomic_ptr_t* value, void* current, void* desired);
SP_API void* sp_atomic_ptr_set(sp_atomic_ptr_t* value, void* desired);
SP_API void* sp_atomic_ptr_get(sp_atomic_ptr_t* value);
```

---

## Formatting (sp_fmt)
```c
SP_API sp_str_r  sp_fmt(sp_mem_t mem, const c8* fmt, ...);
SP_API const c8* sp_fmt_mem_cstr(sp_mem_t mem, const c8* fmt, ...);
SP_API sp_str_r  sp_fmt_mem_v(sp_mem_t mem, sp_str_t fmt, va_list args);
SP_API sp_str_r  sp_fmt_buf(c8* buffer, u64 len, const c8* fmt, ...);
SP_API sp_str_r  sp_fmt_buf_v(c8* buffer, u64 len, sp_str_t fmt, va_list args);
SP_API sp_err_t  sp_fmt_io(sp_io_writer_t* io, const c8* fmt, ...);
SP_API sp_err_t  sp_fmt_io_v(sp_io_writer_t* io, sp_str_t fmt, va_list args);
SP_API void      sp_fmt_render_default(sp_io_writer_t* io, sp_fmt_arg_t* arg, sp_fmt_arg_t* param);
SP_API void      sp_fmt_directive_register(const c8* name, sp_fmt_directive_t directive);
```

### Format Macros
```c
SP_FMT_S8(val)   // s8
SP_FMT_S16(val)  // s16
SP_FMT_S32(val)  // s32
SP_FMT_S64(val)  // s64
SP_FMT_U8(val)   // u8
SP_FMT_U16(val)  // u16
SP_FMT_U32(val)  // u32
SP_FMT_U64(val)  // u64
SP_FMT_F32(val)  // f32
SP_FMT_F64(val)  // f64
SP_FMT_CSTR(val) // const c8*
SP_FMT_STR(val)  // sp_str_t
SP_FMT_BOOL(val) // bool
SP_FMT_CHAR(val) // c8
SP_FMT_PTR(val)  // void*
SP_FMT_ERR(val)  // sp_err_t
```

---

## Logging & Printing
```c
SP_API void sp_log(const c8* fmt, ...);
SP_API void sp_log_str(sp_str_t fmt, ...);
SP_API void sp_log_err(const c8* fmt, ...);
SP_API void sp_print(const c8* fmt, ...);
SP_API void sp_print_str(sp_str_t fmt, ...);
SP_API void sp_print_err(const c8* fmt, ...);
```

---

## Parsing (sp_parse)
```c
SP_API u8        sp_parse_u8(sp_str_t str);
SP_API u16       sp_parse_u16(sp_str_t str);
SP_API u32       sp_parse_u32(sp_str_t str);
SP_API u64       sp_parse_u64(sp_str_t str);
SP_API s8        sp_parse_s8(sp_str_t str);
SP_API s16       sp_parse_s16(sp_str_t str);
SP_API s32       sp_parse_s32(sp_str_t str);
SP_API s64       sp_parse_s64(sp_str_t str);
SP_API f32       sp_parse_f32(sp_str_t str);
SP_API f64       sp_parse_f64(sp_str_t str);
SP_API c8        sp_parse_c8(sp_str_t str);
SP_API u16       sp_parse_c16(sp_str_t str);
SP_API void*     sp_parse_ptr(sp_str_t str);
SP_API bool      sp_parse_bool(sp_str_t str);
SP_API sp_hash_t sp_parse_hash(sp_str_t str);
SP_API u64       sp_parse_hex(sp_str_t str);
SP_API bool      sp_parse_u8_ex(sp_str_t str, u8* out);
SP_API bool      sp_parse_u16_ex(sp_str_t str, u16* out);
SP_API bool      sp_parse_u32_ex(sp_str_t str, u32* out);
SP_API bool      sp_parse_u64_ex(sp_str_t str, u64* out);
SP_API bool      sp_parse_s8_ex(sp_str_t str, s8* out);
SP_API bool      sp_parse_s16_ex(sp_str_t str, s16* out);
SP_API bool      sp_parse_s32_ex(sp_str_t str, s32* out);
SP_API bool      sp_parse_s64_ex(sp_str_t str, s64* out);
SP_API bool      sp_parse_f32_ex(sp_str_t str, f32* out);
SP_API bool      sp_parse_f64_ex(sp_str_t str, f64* out);
SP_API bool      sp_parse_c8_ex(sp_str_t str, c8* out);
SP_API bool      sp_parse_c16_ex(sp_str_t str, u16* out);
SP_API bool      sp_parse_ptr_ex(sp_str_t str, void** out);
SP_API bool      sp_parse_bool_ex(sp_str_t str, bool* out);
SP_API bool      sp_parse_hash_ex(sp_str_t str, sp_hash_t* out);
SP_API bool      sp_parse_hex_ex(sp_str_t str, u64* out);
SP_API bool      sp_parse_is_digit(c8 c);
```

---

## UTF-8 (sp_utf8)
```c
SP_API u32             sp_utf8_decode(const c8* ptr);
SP_API u8              sp_utf8_encode(u32 codepoint, c8* out);
SP_API u8              sp_utf8_num_bytes_from_codepoint(u32 codepoint);
SP_API u8              sp_utf8_num_bytes_from_ptr(const u8* ptr);
SP_API u8              sp_utf8_num_bytes_from_byte(u8 byte);
SP_API sp_utf8_it_t    sp_utf8_it(sp_str_t str);
SP_API sp_utf8_it_t    sp_utf8_rit(sp_str_t str);
SP_API bool            sp_utf8_it_valid(sp_utf8_it_t* it);
SP_API void            sp_utf8_it_next(sp_utf8_it_t* it);
SP_API void            sp_utf8_it_prev(sp_utf8_it_t* it);
SP_API bool            sp_utf8_validate(sp_str_t str);
SP_API bool            sp_utf8_is_byte_ascii(u8 b);
SP_API bool            sp_utf8_is_codepoint_ascii(u32 codepoint);
SP_API u32             sp_utf8_to_upper(u32 codepoint);
SP_API u32             sp_utf8_to_lower(u32 codepoint);
SP_API u32             sp_utf8_num_codepoints(sp_str_t str);
```

---

## WTF-8/WTF-16
```c
SP_API bool            sp_wtf8_validate(sp_str_t str);
SP_API sp_wide_str_t   sp_wtf8_to_wtf16(sp_mem_t mem, sp_str_t wtf8);
SP_API sp_str_t        sp_wtf16_to_wtf8(sp_mem_t mem, sp_wide_str_t wtf16);
SP_API sp_wide_str_t sp_wide_str(const u16* str, u32 len);
```

---

## Environment (sp_env)
```c
SP_API void     sp_env_init(sp_mem_t mem, sp_env_t* env);
SP_API sp_env_t sp_env_capture(sp_mem_t mem);
SP_API sp_env_t sp_env_copy(sp_mem_t mem, sp_env_t* env);
SP_API u32      sp_env_count(sp_env_t* env);
SP_API sp_str_t sp_env_get(sp_env_t* env, sp_str_t name);
SP_API sp_str_t sp_env_get_c(sp_env_t* env, const c8* name);
SP_API bool     sp_env_contains(sp_env_t* env, sp_str_t name);
SP_API bool     sp_env_contains_c(sp_env_t* env, const c8* name);
SP_API void     sp_env_insert(sp_env_t* env, sp_str_t name, sp_str_t value);
SP_API void     sp_env_insert_c(sp_env_t* env, const c8* name, const c8* value);
SP_API void     sp_env_erase(sp_env_t* env, sp_str_t name);
SP_API void     sp_env_erase_c(sp_env_t* env, const c8* name);
SP_API void     sp_env_destroy(sp_env_t* env);
```

---

## Platform (sp_os)
```c
SP_API sp_os_kind_t       sp_os_get_kind();
SP_API sp_fs_path_kind_t  sp_os_get_path_kind();
SP_API sp_str_t       sp_os_get_name();
SP_API sp_str_t       sp_os_get_executable_ext();
SP_API sp_str_t       sp_os_lib_kind_to_extension(sp_os_lib_kind_t kind);
SP_API sp_str_t       sp_os_lib_to_file_name(sp_mem_t mem, sp_str_t lib, sp_os_lib_kind_t kind);
SP_API void           sp_os_sleep_ms(f64 ms);
SP_API void           sp_os_sleep_ns(u64 ns);
SP_API void           sp_os_print(sp_str_t message);
SP_API void           sp_os_print_err(sp_str_t message);
SP_API sp_str_t       sp_os_env_get(sp_str_t key);
SP_API sp_os_env_it_t sp_os_env_it_begin();
SP_API bool           sp_os_env_it_valid(sp_os_env_it_t* it);
SP_API void           sp_os_env_it_next(sp_os_env_it_t* it);
SP_API void           sp_os_register_signal_handler(sp_os_signal_t, sp_os_signal_handler_t, void* userdata);
SP_API bool           sp_os_is_tty(sp_sys_fd_t fd);
SP_API void           sp_os_tty_size(sp_sys_fd_t fd, u32* cols, u32* rows);
SP_API s32            sp_os_tty_enter_raw(sp_sys_fd_t fd, sp_tty_mode_t* saved);
SP_API s32            sp_os_tty_restore(sp_sys_fd_t fd, const sp_tty_mode_t* saved);
SP_API void           sp_os_qsort(void* arr, u64 len, u64 stride, sp_qsort_fn_t);
```

---

## File Monitor (sp_fmon)
```c
SP_API void sp_fmon_init(sp_mem_t mem, sp_fmon_t* m, sp_fmon_fn_t fn, sp_fmon_event_kind_t events, void* user_data);
SP_API void sp_fmon_deinit(sp_fmon_t* monitor);
SP_API void sp_fmon_add_dir(sp_fmon_t* monitor, sp_str_t path);
SP_API void sp_fmon_add_file(sp_fmon_t* monitor, sp_str_t file_path);
SP_API void sp_fmon_process_changes(sp_fmon_t* monitor);
SP_API void sp_fmon_emit_changes(sp_fmon_t* monitor);
```

---

## Application (sp_app)
```c
SP_API sp_app_t*       sp_app_new(sp_mem_t mem, sp_app_config_t config);
SP_API sp_app_result_t sp_app_tick(sp_app_t* app);
SP_API void            sp_app_destroy(sp_app_t* app);
SP_API s32             sp_app_run_locked(sp_app_t* app);
SP_API s32             sp_app_run_free(sp_app_t* app);
SP_API s32             sp_app_run(sp_app_config_t config);
```

---

## System (sp_sys)

Low-level POSIX/Windows system wrappers. Most users should use `sp_fs_*` / `sp_io_*` instead.

```c
SP_API void        sp_sys_init();
SP_API s64         sp_sys_read(sp_sys_fd_t fd, void* buf, u64 count);
SP_API s64         sp_sys_write(sp_sys_fd_t fd, const void* buf, u64 count);
SP_API s64         sp_sys_pread(sp_sys_fd_t fd, void* buf, u64 count, u64 offset);
SP_API s64         sp_sys_pwrite(sp_sys_fd_t fd, const void* buf, u64 count, u64 offset);
SP_API sp_sys_fd_t sp_sys_get_root(s32 it);
SP_API s64         sp_sys_get_exe_path(c8* buf, u64 size);
SP_API s64         sp_sys_get_cwd_path(c8* buf, u64 size);
SP_API s64         sp_sys_get_storage_path(c8* buf, u64 size);
SP_API s64         sp_sys_get_config_path(c8* buf, u64 size);
SP_API sp_sys_fd_t sp_sys_open(sp_sys_fd_t fd, const c8* path, u32 len, s32 flags, s32 mode);
SP_API s32         sp_sys_close(sp_sys_fd_t fd);
SP_API s32         sp_sys_pipe(sp_sys_fd_t* read_end, sp_sys_fd_t* write_end);
SP_API s32         sp_sys_mkdir(sp_sys_fd_t fd, const c8* path, u32 len, s32 mode);
SP_API s32         sp_sys_rmdir(sp_sys_fd_t fd, const c8* path, u32 len);
SP_API s32         sp_sys_unlink(sp_sys_fd_t fd, const c8* path, u32 len);
SP_API s32         sp_sys_rename(sp_sys_fd_t from_fd, const c8* from, u32 from_len, sp_sys_fd_t to_fd, const c8* to, u32 to_len);
SP_API s32         sp_sys_link(sp_sys_fd_t from_fd, const c8* existing, u32 existing_len, sp_sys_fd_t to_fd, const c8* alias, u32 alias_len);
SP_API s32         sp_sys_symlink(const c8* existing, u32 existing_len, sp_sys_fd_t to_fd, const c8* alias, u32 alias_len);
SP_API s32         sp_sys_get_path_metadata(sp_sys_fd_t fd, const c8* path, u32 len, sp_sys_file_meta_t* st);
SP_API s32         sp_sys_get_link_metadata(sp_sys_fd_t fd, const c8* path, u32 len, sp_sys_file_meta_t* st);
SP_API s32         sp_sys_get_file_metadata(sp_sys_fd_t fd, sp_sys_file_meta_t* st);
SP_API s32         sp_sys_chmod(sp_sys_fd_t fd, const c8* path, u32 len, const sp_sys_file_meta_t* st);
SP_API s32         sp_sys_clock_gettime(s32 clockid, sp_sys_timespec_t* ts);
SP_API s32         sp_sys_nanosleep(const sp_sys_timespec_t* req, sp_sys_timespec_t* rem);
SP_API s64         sp_sys_canonicalize_path(const c8* path, u32 len, c8* buf, u64 size);
SP_API s32         sp_sys_fd_ready(sp_sys_fd_t fd, u8* ready);
SP_API s32         sp_sys_fd_wait(sp_sys_fd_t fd);
SP_API s32         sp_sys_fds_wait(const sp_sys_fd_t* fds, u8* ready, u64 nfds);
SP_API void*       sp_sys_alloc(u64 size);
SP_API void        sp_sys_free(void* ptr, u64 size);
SP_API void*       sp_sys_memcpy(void* dest, const void* src, u64 n);
SP_API void*       sp_sys_memmove(void* dest, const void* src, u64 n);
SP_API void*       sp_sys_memset(void* dest, u8 fill, u64 n);
SP_API s32         sp_sys_memcmp(const void* a, const void* b, u64 n);
SP_API void        sp_sys_assert(bool cond);
SP_API void        sp_sys_exit(s32 code);
SP_API void        sp_sys_env(const c8** env, u32* len);
SP_API s64         sp_sys_lseek(sp_sys_fd_t fd, s64 offset, s32 whence);
SP_API s32         sp_sys_chdir(const c8* path, u32 len);
SP_API sp_sys_fd_t sp_sys_open_s(sp_sys_fd_t fd, sp_str_t path, s32 flags, s32 mode);
SP_API s32         sp_sys_get_path_metadata_s(sp_sys_fd_t fd, sp_str_t path, sp_sys_file_meta_t* st);
SP_API s32         sp_sys_get_link_metadata_s(sp_sys_fd_t fd, sp_str_t path, sp_sys_file_meta_t* st);
SP_API s32         sp_sys_mkdir_s(sp_sys_fd_t fd, sp_str_t path, s32 mode);
SP_API s32         sp_sys_rmdir_s(sp_sys_fd_t fd, sp_str_t path);
SP_API s32         sp_sys_unlink_s(sp_sys_fd_t fd, sp_str_t path);
SP_API s32         sp_sys_rename_s(sp_sys_fd_t from_fd, sp_str_t from, sp_sys_fd_t to_fd, sp_str_t to);
SP_API s32         sp_sys_chdir_s(sp_str_t path);
SP_API s32         sp_sys_link_s(sp_sys_fd_t from_fd, sp_str_t existing, sp_sys_fd_t to_fd, sp_str_t alias);
SP_API s32         sp_sys_symlink_s(sp_str_t existing, sp_sys_fd_t to_fd, sp_str_t alias);
SP_API s32         sp_sys_chmod_s(sp_sys_fd_t fd, sp_str_t path, const sp_sys_file_meta_t* st);
SP_API s64         sp_sys_canonicalize_path_s(sp_str_t path, c8* buf, u64 size);
SP_API s32         sp_sys_fs_it_open(sp_sys_fd_t fd, sp_sys_fs_it_t* it, const c8* path, u32 path_len, void* buf, u64 cap);
SP_API s32         sp_sys_fs_it_open_s(sp_sys_fd_t fd, sp_sys_fs_it_t* it, sp_str_t path, sp_mem_slice_t buf);
SP_API s32         sp_sys_fs_it_next(sp_sys_fs_it_t* it, sp_sys_fs_entry_t* out);
SP_API void        sp_sys_fs_it_close(sp_sys_fs_it_t* it);
SP_API sp_nt_status_t sp_sys_nt_path(sp_str_t utf8, sp_sys_nt_path_t* out);
SP_API void           sp_sys_nt_path_free(sp_sys_nt_path_t* path);
```

---

## Error Handling

### Error Type
```c
typedef enum { ... } sp_err_t;
```

### Assertions
```c
SP_API void sp_assert_f(sp_str_t file, sp_str_t line, sp_str_t func, sp_str_t expr, bool cond);
#define sp_assert(expr)  sp_assert_f(...)
```

---

## Quick Lookup by Task

| Task | API |
|------|-----|
| Create string view | `sp_str_view("text")` |
| Allocate string copy | `sp_str_copy(mem, s)` |
| Compare strings | `sp_str_equal(a, b)` |
| Check empty string | `sp_str_empty(str)` |
| Allocate memory | `sp_alloc(mem, size)` |
| Free memory | `sp_free(mem, ptr)` |
| Scratch arena begin | `sp_mem_begin_scratch()` |
| Scratch arena end | `sp_mem_end_scratch(mark)` |
| Format string | `sp_fmt(mem, "{}", SP_FMT_STR(s))` |
| Log message | `sp_log("msg {}", ...)` |
| Print message | `sp_print("msg {}", ...)` |
| Read file | `sp_io_read_file(mem, path, &content)` |
| Write to stdout | `sp_io_write_str(writer, str, &n)` |
| Get stdout writer | `sp_io_get_std_out(&writer)` |
| Check path exists | `sp_fs_exists(path)` |
| Join paths | `sp_fs_join_path(mem, a, b)` |
| Create directory | `sp_fs_create_dir(path)` |
| Remove file | `sp_fs_remove_file(path)` |
| Copy file | `sp_fs_copy(from, to)` |
| Iterate directory | `sp_fs_it_new(mem, path)` |
| Run process | `sp_ps_run(mem, config)` |
| Current time | `sp_tm_now_epoch()` |
| Sleep | `sp_sleep_ms(ms)` |
| Create thread | `sp_thread_init(&thread, fn, ud)` |
| Lock mutex | `sp_mutex_lock(&mutex)` |
| Parse integer | `sp_parse_s32(str)` |
| UTF-8 decode | `sp_utf8_decode(ptr)` |
| Hash string | `sp_hash_cstr(str)` |
| Zero initialize | `SP_ZERO_INITIALIZE()` |
| Array length | `SP_CARR_LEN(arr)` |

---

## Prefix Reference

| Prefix | Meaning |
|--------|---------|
| `sp_` | Public API |
| `sp_str_` | String operations |
| `sp_cstr_` | C string operations |
| `sp_mem_` | Memory management |
| `sp_da_` | Dynamic array internals |
| `sp_ht_` | Hash table internals |
| `sp_io_` | Input/output |
| `sp_fs_` | Filesystem |
| `sp_ps_` | Process/subprocess |
| `sp_tm_` | Time/date |
| `sp_thread_` | Threads |
| `sp_mutex_` | Mutexes |
| `sp_cv_` | Condition variables |
| `sp_semaphore_` | Semaphores |
| `sp_spin_` | Spin locks |
| `sp_atomic_` | Atomic operations |
| `sp_fmt_` | Formatting |
| `sp_log_` / `sp_print_` | Logging/printing |
| `sp_parse_` | String parsing |
| `sp_utf8_` | UTF-8 handling |
| `sp_wtf8_` / `sp_wtf16_` | WTF-8/WTF-16 encoding |
| `sp_env_` | Environment variables |
| `sp_os_` | Platform-specific APIs |
| `sp_fmon_` | File monitoring |
| `sp_app_` | Application framework |
| `sp_sys_` | Low-level system wrappers |
| `sp_hash_` | Hash utilities |
| `SP_` | Macro constants |