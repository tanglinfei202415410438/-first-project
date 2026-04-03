import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

# ==================== 数据库初始化 ====================
def init_db():
    conn = sqlite3.connect('bookstore.db')
    c = conn.cursor()
    # 图书表
    c.execute('''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT,
        publisher TEXT,
        publish_date TEXT,
        stock INTEGER DEFAULT 0
    )''')
    # 供应商表
    c.execute('''CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT,
        type TEXT,
        status TEXT
    )''')
    # 采购订单表
    c.execute('''CREATE TABLE IF NOT EXISTS purchase_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_title TEXT,
        quantity INTEGER,
        order_date TEXT,
        status TEXT
    )''')
    # 销售记录表
    c.execute('''CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_title TEXT,
        quantity INTEGER,
        sale_date TEXT,
        store TEXT
    )''')
    conn.commit()
    conn.close()

# ==================== 图书管理 ====================
class BookManager:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.frame, text="图书管理", font=("Arial", 16)).pack(pady=5)

        # 表单
        form_frame = tk.Frame(self.frame)
        form_frame.pack(pady=5)
        tk.Label(form_frame, text="书名:").grid(row=0, column=0)
        self.title_entry = tk.Entry(form_frame, width=20)
        self.title_entry.grid(row=0, column=1)
        tk.Label(form_frame, text="作者:").grid(row=0, column=2)
        self.author_entry = tk.Entry(form_frame, width=15)
        self.author_entry.grid(row=0, column=3)
        tk.Label(form_frame, text="出版社:").grid(row=0, column=4)
        self.pub_entry = tk.Entry(form_frame, width=15)
        self.pub_entry.grid(row=0, column=5)
        tk.Label(form_frame, text="出版日期:").grid(row=0, column=6)
        self.date_entry = tk.Entry(form_frame, width=12)
        self.date_entry.grid(row=0, column=7)
        tk.Label(form_frame, text="库存:").grid(row=0, column=8)
        self.stock_entry = tk.Entry(form_frame, width=8)
        self.stock_entry.grid(row=0, column=9)

        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="添加", command=self.add_book).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="修改", command=self.update_book).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="删除", command=self.delete_book).pack(side=tk.LEFT, padx=5)

        # 表格显示
        self.tree = ttk.Treeview(self.frame, columns=("ID","书名","作者","出版社","出版日期","库存"), show="headings")
        for col in ("ID","书名","作者","出版社","出版日期","库存"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.refresh_table()

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = sqlite3.connect('bookstore.db')
        c = conn.cursor()
        c.execute("SELECT * FROM books")
        for row in c.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def add_book(self):
        title = self.title_entry.get()
        if not title:
            messagebox.showerror("错误", "书名不能为空")
            return
        author = self.author_entry.get()
        publisher = self.pub_entry.get()
        pub_date = self.date_entry.get()
        try:
            stock = int(self.stock_entry.get())
        except:
            stock = 0
        conn = sqlite3.connect('bookstore.db')
        c = conn.cursor()
        c.execute("INSERT INTO books (title, author, publisher, publish_date, stock) VALUES (?,?,?,?,?)",
                  (title, author, publisher, pub_date, stock))
        conn.commit()
        conn.close()
        self.clear_entries()
        self.refresh_table()

    def update_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("错误", "请先选择要修改的图书")
            return
        book_id = self.tree.item(selected[0])['values'][0]
        title = self.title_entry.get()
        author = self.author_entry.get()
        publisher = self.pub_entry.get()
        pub_date = self.date_entry.get()
        try:
            stock = int(self.stock_entry.get())
        except:
            stock = 0
        conn = sqlite3.connect('bookstore.db')
        c = conn.cursor()
        c.execute("UPDATE books SET title=?, author=?, publisher=?, publish_date=?, stock=? WHERE id=?",
                  (title, author, publisher, pub_date, stock, book_id))
        conn.commit()
        conn.close()
        self.clear_entries()
        self.refresh_table()

    def delete_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("错误", "请先选择要删除的图书")
            return
        book_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("确认", "确定删除该图书吗？"):
            conn = sqlite3.connect('bookstore.db')
            c = conn.cursor()
            c.execute("DELETE FROM books WHERE id=?", (book_id,))
            conn.commit()
            conn.close()
            self.refresh_table()
            self.clear_entries()

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])['values']
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, values[1])
            self.author_entry.delete(0, tk.END)
            self.author_entry.insert(0, values[2])
            self.pub_entry.delete(0, tk.END)
            self.pub_entry.insert(0, values[3])
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, values[4])
            self.stock_entry.delete(0, tk.END)
            self.stock_entry.insert(0, values[5])

    def clear_entries(self):
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.pub_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.stock_entry.delete(0, tk.END)

# ==================== 供应商管理 ====================
class SupplierManager:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.frame, text="供应商管理", font=("Arial", 16)).pack(pady=5)

        form_frame = tk.Frame(self.frame)
        form_frame.pack(pady=5)
        tk.Label(form_frame, text="名称:").grid(row=0, column=0)
        self.name_entry = tk.Entry(form_frame)
        self.name_entry.grid(row=0, column=1)
        tk.Label(form_frame, text="联系方式:").grid(row=0, column=2)
        self.contact_entry = tk.Entry(form_frame)
        self.contact_entry.grid(row=0, column=3)
        tk.Label(form_frame, text="类型:").grid(row=0, column=4)
        self.type_entry = tk.Entry(form_frame)
        self.type_entry.grid(row=0, column=5)
        tk.Label(form_frame, text="状态:").grid(row=0, column=6)
        self.status_entry = tk.Entry(form_frame)
        self.status_entry.grid(row=0, column=7)

        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="添加", command=self.add_supplier).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="修改", command=self.update_supplier).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="删除", command=self.delete_supplier).pack(side=tk.LEFT, padx=5)

        self.tree = ttk.Treeview(self.frame, columns=("ID","名称","联系方式","类型","状态"), show="headings")
        for col in ("ID","名称","联系方式","类型","状态"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.refresh_table()

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = sqlite3.connect('bookstore.db')
        c = conn.cursor()
        c.execute("SELECT * FROM suppliers")
        for row in c.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def add_supplier(self):
        name = self.name_entry.get()
        if not name:
            messagebox.showerror("错误", "名称不能为空")
            return
        contact = self.contact_entry.get()
        stype = self.type_entry.get()
        status = self.status_entry.get()
        conn = sqlite3.connect('bookstore.db')
        c = conn.cursor()
        c.execute("INSERT INTO suppliers (name, contact, type, status) VALUES (?,?,?,?)",
                  (name, contact, stype, status))
        conn.commit()
        conn.close()
        self.refresh_table()
        self.clear_entries()

    def update_supplier(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("错误", "请先选择供应商")
            return
        sid = self.tree.item(selected[0])['values'][0]
        name = self.name_entry.get()
        contact = self.contact_entry.get()
        stype = self.type_entry.get()
        status = self.status_entry.get()
        conn = sqlite3.connect('bookstore.db')
        c = conn.cursor()
        c.execute("UPDATE suppliers SET name=?, contact=?, type=?, status=? WHERE id=?", 
                  (name, contact, stype, status, sid))
        conn.commit()
        conn.close()
        self.refresh_table()
        self.clear_entries()

    def delete_supplier(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("错误", "请先选择供应商")
            return
        sid = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("确认", "确定删除该供应商吗？"):
            conn = sqlite3.connect('bookstore.db')
            c = conn.cursor()
            c.execute("DELETE FROM suppliers WHERE id=?", (sid,))
            conn.commit()
            conn.close()
            self.refresh_table()
            self.clear_entries()

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])['values']
            self.name_entry.delete(0, tk.END); self.name_entry.insert(0, values[1])
            self.contact_entry.delete(0, tk.END); self.contact_entry.insert(0, values[2])
            self.type_entry.delete(0, tk.END); self.type_entry.insert(0, values[3])
            self.status_entry.delete(0, tk.END); self.status_entry.insert(0, values[4])

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.contact_entry.delete(0, tk.END)
        self.type_entry.delete(0, tk.END)
        self.status_entry.delete(0, tk.END)

# ==================== 采购入库 ====================
class PurchaseManager:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.frame, text="采购入库", font=("Arial", 16)).pack(pady=5)

        form_frame = tk.Frame(self.frame)
        form_frame.pack(pady=5)
        tk.Label(form_frame, text="图书名称:").grid(row=0, column=0)
        self.book_entry = tk.Entry(form_frame)
        self.book_entry.grid(row=0, column=1)
        tk.Label(form_frame, text="数量:").grid(row=0, column=2)
        self.qty_entry = tk.Entry(form_frame)
        self.qty_entry.grid(row=0, column=3)

        tk.Button(self.frame, text="添加采购订单", command=self.add_purchase).pack(pady=5)

        self.tree = ttk.Treeview(self.frame, columns=("ID","图书名称","数量","订单日期","状态"), show="headings")
        for col in ("ID","图书名称","数量","订单日期","状态"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

        tk.Button(self.frame, text="确认入库（选中订单）", command=self.confirm_stock_in).pack(pady=5)
        self.refresh_table()

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = sqlite3.connect('bookstore.db')
        c = conn.cursor()
        c.execute("SELECT * FROM purchase_orders")
        for row in c.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def add_purchase(self):
        book_title = self.book_entry.get()
        qty_str = self.qty_entry.get()
        if not book_title or not qty_str:
            messagebox.showerror("错误", "请填写完整")
            return
        try:
            qty = int(qty_str)
        except:
            messagebox.showerror("错误", "数量必须是整数")
            return
        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "已下单"
        conn = sqlite3.connect('bookstore.db')
        c = conn.cursor()
        c.execute("INSERT INTO purchase_orders (book_title, quantity, order_date, status) VALUES (?,?,?,?)",
                  (book_title, qty, order_date, status))
        conn.commit()
        conn.close()
        self.book_entry.delete(0, tk.END)
        self.qty_entry.delete(0, tk.END)
        self.refresh_table()
        messagebox.showinfo("成功", "采购订单已添加")

    def confirm_stock_in(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("错误", "请先选择一个采购订单")
            return
        order_id = self.tree.item(selected[0])['values'][0]
        conn = sqlite3.connect('bookstore.db')
        c = conn.cursor()
        c.execute("SELECT book_title, quantity, status FROM purchase_orders WHERE id=?", (order_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            return
        if row[2] == "已入库":
            messagebox.showinfo("提示", "该订单已经入库过")
            conn.close()
            return
        book_title, qty, _ = row
        # 增加库存
        c.execute("UPDATE books SET stock = stock + ? WHERE title=?", (qty, book_title))
        if c.rowcount == 0:
            messagebox.showerror("错误", f"系统中不存在图书《{book_title}》，请先添加图书信息")
            conn.close()
            return
        c.execute("UPDATE purchase_orders SET status='已入库' WHERE id=?", (order_id,))
        conn.commit()
        conn.close()
        self.refresh_table()
        messagebox.showinfo("成功", f"已为《{book_title}》增加库存 {qty} 本")

# ==================== 销售管理 ====================
class SaleManager:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.frame, text="销售管理", font=("Arial", 16)).pack(pady=5)

        form_frame = tk.Frame(self.frame)
        form_frame.pack(pady=5)
        tk.Label(form_frame, text="图书名称:").grid(row=0, column=0)
        self.book_entry = tk.Entry(form_frame)
        self.book_entry.grid(row=0, column=1)
        tk.Label(form_frame, text="销售数量:").grid(row=0, column=2)
        self.qty_entry = tk.Entry(form_frame)
        self.qty_entry.grid(row=0, column=3)
        tk.Label(form_frame, text="门店:").grid(row=0, column=4)
        self.store_entry = tk.Entry(form_frame)
        self.store_entry.grid(row=0, column=5)

        tk.Button(self.frame, text="销售出库", command=self.sell_book).pack(pady=5)

        self.tree = ttk.Treeview(self.frame, columns=("ID","图书名称","数量","销售日期","门店"), show="headings")
        for col in ("ID","图书名称","数量","销售日期","门店"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)
        self.refresh_table()

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = sqlite3.connect('bookstore.db')
        c = conn.cursor()
        c.execute("SELECT * FROM sales")
        for row in c.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def sell_book(self):
        title = self.book_entry.get()
        qty_str = self.qty_entry.get()
        store = self.store_entry.get()
        if not title or not qty_str:
            messagebox.showerror("错误", "请填写完整")
            return
        try:
            qty = int(qty_str)
        except:
            messagebox.showerror("错误", "数量必须是整数")
            return
        if qty <= 0:
            messagebox.showerror("错误", "数量必须大于0")
            return
        conn = sqlite3.connect('bookstore.db')
        c = conn.cursor()
        c.execute("SELECT stock FROM books WHERE title=?", (title,))
        row = c.fetchone()
        if not row:
            messagebox.showerror("错误", f"图书《{title}》不存在")
            conn.close()
            return
        if row[0] < qty:
            messagebox.showerror("错误", f"库存不足，当前库存为 {row[0]}")
            conn.close()
            return
        # 扣减库存
        c.execute("UPDATE books SET stock = stock - ? WHERE title=?", (qty, title))
        # 记录销售
        sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO sales (book_title, quantity, sale_date, store) VALUES (?,?,?,?)",
                  (title, qty, sale_date, store))
        conn.commit()
        conn.close()
        self.book_entry.delete(0, tk.END)
        self.qty_entry.delete(0, tk.END)
        self.store_entry.delete(0, tk.END)
        self.refresh_table()
        messagebox.showinfo("成功", f"销售 {title} x{qty} 成功")

# ==================== 库存查询 ====================
class StockQuery:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.frame, text="库存查询", font=("Arial", 16)).pack(pady=5)

        search_frame = tk.Frame(self.frame)
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="按书名/作者/出版社搜索:").pack(side=tk.LEFT)
        self.keyword_entry = tk.Entry(search_frame, width=30)
        self.keyword_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="搜索", command=self.search).pack(side=tk.LEFT)

        self.tree = ttk.Treeview(self.frame, columns=("ID","书名","作者","出版社","出版日期","库存"), show="headings")
        for col in ("ID","书名","作者","出版社","出版日期","库存"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)
        self.refresh_all()

    def refresh_all(self):
        self.keyword_entry.delete(0, tk.END)
        self.search()

    def search(self):
        keyword = self.keyword_entry.get()
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = sqlite3.connect('bookstore.db')
        c = conn.cursor()
        if keyword:
            c.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR publisher LIKE ?",
                      (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        else:
            c.execute("SELECT * FROM books")
        for row in c.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()

# ==================== 主程序 ====================
class MainApp:
    def __init__(self, root):
        self.root = root
        root.title("图书库存管理系统")
        root.geometry("1000x600")

        # 创建选项卡
        self.tab_control = ttk.Notebook(root)
        self.tab_control.pack(fill=tk.BOTH, expand=True)

        self.book_tab = tk.Frame(self.tab_control)
        self.supplier_tab = tk.Frame(self.tab_control)
        self.purchase_tab = tk.Frame(self.tab_control)
        self.sale_tab = tk.Frame(self.tab_control)
        self.query_tab = tk.Frame(self.tab_control)

        self.tab_control.add(self.book_tab, text="图书管理")
        self.tab_control.add(self.supplier_tab, text="供应商管理")
        self.tab_control.add(self.purchase_tab, text="采购入库")
        self.tab_control.add(self.sale_tab, text="销售管理")
        self.tab_control.add(self.query_tab, text="库存查询")

        # 初始化各个模块
        self.book_mgr = BookManager(self.book_tab)
        self.supplier_mgr = SupplierManager(self.supplier_tab)
        self.purchase_mgr = PurchaseManager(self.purchase_tab)
        self.sale_mgr = SaleManager(self.sale_tab)
        self.stock_query = StockQuery(self.query_tab)

if __name__ == "__main__":
    init_db()   # 初始化数据库和表
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
