








def table_control(func):
    def wapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"无法控制表格: {e}")
            import traceback
            traceback.print_exc()
            return None
    return wapper
@table_control