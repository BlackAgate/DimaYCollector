
def get_human_readable(size):
    suffixes = ["bytes", "KB", "MB", "GB", "TB", "PB"]
    idx = 0
    while size >= 1024:
        size /= 1024
        idx += 1
    if idx == 0:
        return "{:.0f} {}".format(size, suffixes[idx])
    return "{:.2f} {}".format(size, suffixes[idx])


def clean_dirname(dirname):
    dirname = dirname.replace(":", "")
    if dirname[0] == '/':  # remove leading slash for os.path.join to work properly
        dirname = dirname[1:]
    return dirname