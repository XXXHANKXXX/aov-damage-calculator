import tkinter as tk
from tkinter import ttk, messagebox
import ctypes

# 嘗試啟用 Windows 高解析度 DPI 支援，解決文字模糊問題
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

ITEMS_DATA = [
    {'id': 'item1', 'name': '鋼鐵長槍', 'desc': '造成傷害減少目標6%物防，最多疊加4層', 'exclusiveGroup': None},
    {'id': 'item2', 'name': '龍骨劍', 'desc': '普攻附帶目標當前生命值8%物傷', 'exclusiveGroup': None},
    {'id': 'item3', 'name': '聖劍', 'desc': '+25% 暴擊率 / 暴擊傷害 +40%', 'exclusiveGroup': None},
    {'id': 'item4', 'name': '天叢雲之刃', 'desc': '物穿+35% (唯一被動：穿刺)', 'exclusiveGroup': '穿刺'},
    {'id': 'item5', 'name': '颶風雙刀', 'desc': '+25% 暴擊率', 'exclusiveGroup': None},
    {'id': 'item6', 'name': '王者之劍', 'desc': '對生命值低於50%的敵人造成額外30%傷害', 'exclusiveGroup': None},
    {'id': 'item7', 'name': '雷電戟', 'desc': '普攻附帶45~87魔傷 / 每3擊觸發閃電鏈造成150~430魔傷', 'exclusiveGroup': None},
    {'id': 'item8', 'name': '炎怒之爪', 'desc': '+20% 暴擊率', 'exclusiveGroup': None},
    {'id': 'item9', 'name': '晨星', 'desc': '+10% 暴擊率 / 普攻附帶50物傷(遠程100) / 物穿+20%(遠程40%)(唯一被動：穿刺)', 'exclusiveGroup': '穿刺'},
    {'id': 'item11', 'name': '隱襲手弩', 'desc': '+20% 暴擊率', 'exclusiveGroup': None},
    {'id': 'item12', 'name': '嗜血弓', 'desc': '+10% 暴擊率', 'exclusiveGroup': None},
    {'id': 'item10', 'name': '日影之弓', 'desc': '+10% 暴擊率 / 普攻附帶50物傷(遠程100)', 'exclusiveGroup': None}
]

class AoVCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("傳說對決 普攻物傷計算器")
        self.root.geometry("1450x850")

        self.style = ttk.Style()
        self.style.theme_use("default")

        self.panels = []
        self.panel_counter = 0
        self._resizing = False

        # 註冊輸入驗證函數
        self.vcmd_positive_int = (self.root.register(self.validate_positive_int), '%P')
        self.vcmd_positive_float = (self.root.register(self.validate_positive_float), '%P')

        self.setup_ui()
        self.add_panel() # 預設只建立第一個面板

    def validate_positive_int(self, new_val):
        """僅允許空字串、單獨的 '0'，或不以 '0' 開頭的正整數（禁止前導零）"""
        if new_val == "":
            return True
        if new_val.isdigit():
            if len(new_val) > 1 and new_val[0] == '0':
                return False
            return True
        return False

    def validate_positive_float(self, new_val):
        """允許小數點輸入（非負浮點數），且禁止前導零（如 05.5）"""
        if new_val == "":
            return True
        # 不允許僅輸入多個點或無效前導零
        if new_val.count('.') > 1:
            return False
        if new_val.startswith('.'):
            return False
        if len(new_val) > 1 and new_val.startswith('0') and not new_val.startswith('0.'):
            return False
        
        # 允許正在輸入小數點的狀態（如 "12."）
        if new_val.endswith('.'):
            base = new_val[:-1]
            return base.isdigit() or base == ""
        
        try:
            val = float(new_val)
            return val >= 0
        except ValueError:
            return False

    def validate_hero_level_input(self, new_val):
        if new_val == "":
            return True
        if new_val.isdigit():
            if len(new_val) > 1 and new_val[0] == '0':
                return False
            val = int(new_val)
            return 1 <= val <= 15
        return False

    def on_level_focus_out(self, event, panel):
        try:
            val = int(panel['hero_level'].get() or 1)
            if val < 1:
                panel['hero_level'].set(1)
            elif val > 15:
                panel['hero_level'].set(15)
            else:
                panel['hero_level'].set(val)
        except (tk.TclError, ValueError):
            panel['hero_level'].set(1)
        self.on_panel_input_changed(panel)

    def get_var_int(self, var):
        """安全取得整數欄位數值"""
        try:
            val = str(var.get()).strip()
            return int(val) if val.isdigit() else 0
        except Exception:
            return 0

    def get_var_float(self, var):
        """安全取得浮點數/小數欄位數值"""
        try:
            val = str(var.get()).strip()
            return float(val) if val else 0.0
        except Exception:
            return 0.0

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 頂部：共用防守方屬性與控制列
        top_control_frame = ttk.Frame(main_frame)
        top_control_frame.pack(fill=tk.X, pady=(0, 10))

        card_target = ttk.LabelFrame(top_control_frame, text=" 防守方屬性 ", padding=8)
        card_target.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        target_grid = ttk.Frame(card_target)
        target_grid.pack(fill=tk.X)

        ttk.Label(target_grid, text="目標最大生命值:").grid(row=0, column=0, sticky="w", padx=4)
        self.var_target_hp = tk.StringVar(value="0")
        ent_hp = ttk.Entry(target_grid, textvariable=self.var_target_hp, width=12, validate="key", validatecommand=self.vcmd_positive_int)
        ent_hp.grid(row=0, column=1, sticky="w", padx=4)
        ent_hp.bind("<KeyRelease>", lambda e: self.on_global_input_changed())

        ttk.Label(target_grid, text="目標物理防禦:").grid(row=0, column=2, sticky="w", padx=4)
        self.var_target_armor = tk.StringVar(value="0")
        ent_arm = ttk.Entry(target_grid, textvariable=self.var_target_armor, width=12, validate="key", validatecommand=self.vcmd_positive_int)
        ent_arm.grid(row=0, column=3, sticky="w", padx=4)
        ent_arm.bind("<KeyRelease>", lambda e: self.on_global_input_changed())

        ttk.Label(target_grid, text="目標魔法防禦:").grid(row=0, column=4, sticky="w", padx=4)
        self.var_target_marmor = tk.StringVar(value="0")
        ent_marm = ttk.Entry(target_grid, textvariable=self.var_target_marmor, width=12, validate="key", validatecommand=self.vcmd_positive_int)
        ent_marm.grid(row=0, column=5, sticky="w", padx=4)
        ent_marm.bind("<KeyRelease>", lambda e: self.on_global_input_changed())

        # 新增面板按鈕
        btn_add_panel = ttk.Button(top_control_frame, text="➕ 新增對照面板", command=self.add_panel)
        btn_add_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=2)

        # 側邊可調整大小的容器
        self.paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(side="top", fill="both", expand=True, pady=(0, 5))
        self.paned_window.bind("<Configure>", lambda e: self.balance_panes())

    def balance_panes(self):
        if self._resizing:
            return
        self._resizing = True
        self.root.update_idletasks()
        total_width = self.paned_window.winfo_width()
        n = len(self.panels)
        if n <= 1 or total_width <= 1:
            self._resizing = False
            return
        pane_width = total_width / n
        for i in range(n - 1):
            pos = int((i + 1) * pane_width)
            try:
                self.paned_window.sashpos(i, pos)
            except Exception:
                pass
        self._resizing = False

    def add_panel(self):
        # 修改上限檢查從 5 改為 10
        if len(self.panels) >= 10:
            messagebox.showwarning("提示", "最多只能開啟 10 個對照面板！")
            return

        self.panel_counter += 1
        panel_id = len(self.panels) + 1

        panel_frame = ttk.LabelFrame(self.paned_window, padding=8)
        self.paned_window.add(panel_frame)

        # 面板頂部標題列與右上角紅叉關閉按鈕
        header_bar = ttk.Frame(panel_frame)
        header_bar.pack(fill=tk.X, pady=(0, 4))

        title_lbl = ttk.Label(header_bar, text=f"面板 {panel_id}", font=("Arial", 10, "bold"))
        title_lbl.pack(side=tk.LEFT)

        p_data = {
            'id': panel_id,
            'panel_frame': panel_frame,
            'title_label': title_lbl,
            'desc_labels': [],
            'combobox_widgets': {},
            'user_hit_modes': {},
            'item_vars': {},
            'item_cb_widgets': {}
        }

        btn_close = tk.Button(
            header_bar, text="❌", fg="red", relief="flat",
            bg=self.style.lookup("TFrame", "background") or "#f0f0f0",
            command=lambda: self.close_panel(p_data), cursor="hand2", font=("Arial", 9, "bold")
        )
        btn_close.pack(side=tk.RIGHT)

        # 1. 攻擊方屬性
        card1 = ttk.LabelFrame(panel_frame, text=" 1. 攻擊方屬性 ", padding=6)
        card1.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(card1, text="英雄等級:").grid(row=0, column=0, sticky="w", pady=2)
        p_data['hero_level'] = tk.StringVar(value="1")
        vcmd_lvl = (self.root.register(self.validate_hero_level_input), '%P')
        sp_level = ttk.Spinbox(
            card1, from_=1, to=15, textvariable=p_data['hero_level'], width=10,
            command=lambda: self.on_panel_input_changed(p_data), validate="key", validatecommand=vcmd_lvl
        )
        sp_level.grid(row=0, column=1, sticky="e", pady=2)
        sp_level.bind("<KeyRelease>", lambda e: self.on_panel_input_changed(p_data))
        sp_level.bind("<FocusOut>", lambda e: [self.on_level_focus_out(e, p_data)])
        sp_level.bind("<Return>", lambda e: [self.on_level_focus_out(e, p_data)])

        ttk.Label(card1, text="攻擊範圍:").grid(row=1, column=0, sticky="w", pady=2)
        p_data['hero_type'] = tk.StringVar(value="近戰")
        cb_type = ttk.Combobox(card1, textvariable=p_data['hero_type'], values=["近戰", "遠程"], state="readonly", width=9)
        cb_type.grid(row=1, column=1, sticky="e", pady=2)
        cb_type.bind("<<ComboboxSelected>>", lambda e: [e.widget.selection_clear(), self.on_panel_input_changed(p_data)])

        ttk.Label(card1, text="面板物理攻擊力:").grid(row=2, column=0, sticky="w", pady=2)
        p_data['hero_ad'] = tk.StringVar(value="0")
        ent_ad = ttk.Entry(card1, textvariable=p_data['hero_ad'], width=10, validate="key", validatecommand=self.vcmd_positive_int)
        ent_ad.grid(row=2, column=1, sticky="e", pady=2)
        ent_ad.bind("<KeyRelease>", lambda e: self.on_panel_input_changed(p_data))

        ttk.Label(card1, text="固定物穿:").grid(row=3, column=0, sticky="w", pady=2)
        p_data['flat_pierce'] = tk.StringVar(value="0")
        ent_fp = ttk.Entry(card1, textvariable=p_data['flat_pierce'], width=10, validate="key", validatecommand=self.vcmd_positive_int)
        ent_fp.grid(row=3, column=1, sticky="e", pady=2)
        ent_fp.bind("<KeyRelease>", lambda e: self.on_panel_input_changed(p_data))

        ttk.Label(card1, text="奧義暴擊率(%):").grid(row=4, column=0, sticky="w", pady=2)
        p_data['arcana_crit_rate'] = tk.StringVar(value="0")
        ent_acr = ttk.Entry(card1, textvariable=p_data['arcana_crit_rate'], width=10, validate="key", validatecommand=self.vcmd_positive_float)
        ent_acr.grid(row=4, column=1, sticky="e", pady=2)
        ent_acr.bind("<KeyRelease>", lambda e: self.on_panel_input_changed(p_data))

        ttk.Label(card1, text="奧義暴擊傷害(%):").grid(row=5, column=0, sticky="w", pady=2)
        p_data['arcana_crit_dmg'] = tk.StringVar(value="0")
        ent_acd = ttk.Entry(card1, textvariable=p_data['arcana_crit_dmg'], width=10, validate="key", validatecommand=self.vcmd_positive_float)
        ent_acd.grid(row=5, column=1, sticky="e", pady=2)
        ent_acd.bind("<KeyRelease>", lambda e: self.on_panel_input_changed(p_data))

        p_data['rune_axe'] = tk.BooleanVar(value=False)
        cb_axe = ttk.Checkbutton(card1, text="魔紋：犧牲之斧", variable=p_data['rune_axe'], command=lambda: self.on_panel_input_changed(p_data))
        cb_axe.grid(row=6, column=0, columnspan=2, sticky="w", pady=2)

        p_data['rune_blessing'] = tk.BooleanVar(value=False)
        cb_bless = ttk.Checkbutton(card1, text="魔紋：祝福", variable=p_data['rune_blessing'], command=lambda: self.on_panel_input_changed(p_data))
        cb_bless.grid(row=7, column=0, columnspan=2, sticky="w", pady=2)

        # 2. 裝備選擇面板
        card2 = ttk.LabelFrame(panel_frame, text=" 2. 裝備選擇 ", padding=6)
        card2.pack(fill=tk.X, pady=(0, 6))

        header_frame = ttk.Frame(card2)
        header_frame.pack(fill=tk.X, pady=(0, 4))

        btn_clear = ttk.Button(header_frame, text="清空裝備", command=lambda: self.clear_panel_items(p_data), width=8)
        btn_clear.pack(side=tk.LEFT)

        p_data['lbl_selected_count'] = ttk.Label(header_frame, text="已選: 0/6", font=("Arial", 9, "bold"))
        p_data['lbl_selected_count'].pack(side=tk.RIGHT)

        bg_color = self.style.lookup("TFrame", "background") or "#f0f0f0"
        equip_container = ttk.Frame(card2)
        equip_container.pack(fill=tk.X)

        equip_canvas = tk.Canvas(equip_container, borderwidth=0, background=bg_color, highlightthickness=0, height=140)
        scrollbar_item = ttk.Scrollbar(equip_container, orient="vertical", command=equip_canvas.yview)
        
        scrollable_items_frame = ttk.Frame(equip_canvas, style="TFrame")
        scrollable_items_frame.bind("<Configure>", lambda e: equip_canvas.configure(scrollregion=equip_canvas.bbox("all")))

        canvas_window = equip_canvas.create_window((0, 0), window=scrollable_items_frame, anchor="nw")
        equip_canvas.bind("<Configure>", lambda e, cw=canvas_window: self.on_equip_canvas_configure(e, cw, p_data))
        equip_canvas.configure(yscrollcommand=scrollbar_item.set)

        scrollbar_item.pack(side="right", fill="y")
        equip_canvas.pack(side="left", fill="both", expand=True)

        for item in ITEMS_DATA:
            var = tk.BooleanVar(value=False)
            p_data['item_vars'][item['id']] = var

            frame_item = ttk.Frame(scrollable_items_frame, padding=(1, 2))
            frame_item.pack(fill=tk.X, expand=True, anchor="w")

            tag = f" [{item['exclusiveGroup']}被動互斥]" if item['exclusiveGroup'] else ""
            cb = ttk.Checkbutton(
                frame_item,
                text=f"{item['name']}{tag}",
                variable=var,
                command=lambda i_id=item['id']: self.handle_item_change(p_data, i_id)
            )
            cb.pack(anchor="w")
            p_data['item_cb_widgets'][item['id']] = cb

            lbl_desc = ttk.Label(frame_item, text=f"  ↳ {item['desc']}", foreground="#555555", justify="left", wraplength=280)
            lbl_desc.pack(anchor="w", padx=4, fill=tk.X, expand=True)
            p_data['desc_labels'].append(lbl_desc)

        def bind_mouse_wheel(widget, canvas):
            def _on_wheel(event):
                if event.delta:
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                elif event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")
                return "break"
            
            widget.bind("<MouseWheel>", _on_wheel)
            widget.bind("<Button-4>", _on_wheel)
            widget.bind("<Button-5>", _on_wheel)
            for child in widget.winfo_children():
                bind_mouse_wheel(child, canvas)

        bind_mouse_wheel(scrollable_items_frame, equip_canvas)
        bind_mouse_wheel(equip_canvas, equip_canvas)

        # 3. 計算結果與傷害明細
        card3 = ttk.LabelFrame(panel_frame, text=" 3. 計算結果與傷害明細 ", padding=6)
        card3.pack(fill=tk.BOTH, expand=True)

        control_sub = ttk.Frame(card3)
        control_sub.pack(fill=tk.X, pady=(0, 4))

        ttk.Label(control_sub, text="暴擊計算模式：").pack(side=tk.LEFT)
        p_data['calc_mode'] = tk.StringVar(value="期望值計算模式")
        cb_mode = ttk.Combobox(
            control_sub, textvariable=p_data['calc_mode'],
            values=["期望值計算模式", "手動控制模式"], state="readonly", width=13
        )
        cb_mode.pack(side=tk.LEFT, padx=4)
        cb_mode.bind("<<ComboboxSelected>>", lambda e: [e.widget.selection_clear(), self.calculate_panel(p_data)])
        p_data['cb_calc_mode'] = cb_mode

        stats_frame = tk.Frame(card3, bg="#2c3e50", padx=6, pady=6)
        stats_frame.pack(fill=tk.X, pady=(0, 4))

        p_data['lbl_crit_rate'] = tk.Label(stats_frame, text="總暴擊率：0%", bg="#2c3e50", fg="#f1c40f", font=("Arial", 10, "bold"))
        p_data['lbl_crit_rate'].grid(row=0, column=0, sticky="w", padx=6, pady=2)

        p_data['lbl_crit_dmg'] = tk.Label(stats_frame, text="暴傷倍率：200%", bg="#2c3e50", fg="#f1c40f", font=("Arial", 10, "bold"))
        p_data['lbl_crit_dmg'].grid(row=0, column=1, sticky="w", padx=6, pady=2)

        p_data['lbl_eff_armor'] = tk.Label(stats_frame, text="有效物防：0", bg="#2c3e50", fg="#ffffff", font=("Arial", 10))
        p_data['lbl_eff_armor'].grid(row=1, column=0, sticky="w", padx=6, pady=2)

        p_data['lbl_armor_red'] = tk.Label(stats_frame, text="物防減傷：0%", bg="#2c3e50", fg="#ffffff", font=("Arial", 10))
        p_data['lbl_armor_red'].grid(row=1, column=1, sticky="w", padx=6, pady=2)

        summary_sub = tk.Frame(card3, bg="#2c3e50")
        summary_sub.pack(fill=tk.X, pady=(0, 4))

        p_data['card_min'] = tk.Frame(summary_sub, bg="#34495e", padx=6, pady=4)
        p_data['card_min'].pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=1)
        tk.Label(p_data['card_min'], text="全暴擊普攻次數", bg="#34495e", fg="#cccccc", font=("Arial", 9)).pack()
        p_data['lbl_min_hits'] = tk.Label(p_data['card_min'], text="0 次", bg="#34495e", fg="#2ecc71", font=("Arial", 12, "bold"))
        p_data['lbl_min_hits'].pack()

        p_data['card_avg'] = tk.Frame(summary_sub, bg="#34495e", padx=6, pady=4)
        p_data['card_avg'].pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=1)
        p_data['lbl_label_avg'] = tk.Label(p_data['card_avg'], text="期望值普攻次數", bg="#34495e", fg="#cccccc", font=("Arial", 9))
        p_data['lbl_label_avg'].pack()
        p_data['lbl_avg_hits'] = tk.Label(p_data['card_avg'], text="0 次", bg="#34495e", fg="#00d2d3", font=("Arial", 12, "bold"))
        p_data['lbl_avg_hits'].pack()

        p_data['card_max'] = tk.Frame(summary_sub, bg="#34495e", padx=6, pady=4)
        p_data['card_max'].pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=1)
        tk.Label(p_data['card_max'], text="無暴擊普攻次數", bg="#34495e", fg="#cccccc", font=("Arial", 9)).pack()
        p_data['lbl_max_hits'] = tk.Label(p_data['card_max'], text="0 次", bg="#34495e", fg="#e74c3c", font=("Arial", 12, "bold"))
        p_data['lbl_max_hits'].pack()

        tree_container = ttk.Frame(card3)
        tree_container.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(tree_container, show="headings", height=10)
        tree_scroll_y = ttk.Scrollbar(tree_container, orient="vertical", command=tree.yview)
        tree_scroll_x = ttk.Scrollbar(tree_container, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        p_data['tree'] = tree
        tree.bind("<Configure>", lambda e: self.update_combobox_positions(p_data))
        tree_scroll_y.config(command=lambda *args: [tree.yview(*args), self.update_combobox_positions(p_data)])

        self.panels.append(p_data)
        self.balance_panes()
        self.calculate_panel(p_data)

    def close_panel(self, p_data):
        if len(self.panels) <= 1:
            messagebox.showwarning("提示", "必須保留至少一個面板！")
            return
        self.clear_comboboxes(p_data)
        self.paned_window.remove(p_data['panel_frame'])
        p_data['panel_frame'].destroy()
        self.panels.remove(p_data)

        for idx, panel in enumerate(self.panels):
            new_id = idx + 1
            panel['id'] = new_id
            panel['title_label'].config(text=f"面板 {new_id}")

        self.balance_panes()
        self.calculate_all_panels()

    def clear_panel_items(self, p_data):
        p_data['user_hit_modes'].clear()
        for var in p_data['item_vars'].values():
            var.set(False)
        self.handle_item_change(p_data, None)

    def on_equip_canvas_configure(self, event, canvas_window, p_data):
        event.widget.itemconfig(canvas_window, width=event.width)
        new_wrap_width = max(100, event.width - 30)
        for lbl in p_data['desc_labels']:
            lbl.config(wraplength=new_wrap_width)

    def clear_comboboxes(self, p_data):
        for cb in p_data['combobox_widgets'].values():
            try:
                cb.destroy()
            except Exception:
                pass
        p_data['combobox_widgets'].clear()

    def update_combobox_positions(self, p_data):
        for hit_idx, cb in p_data['combobox_widgets'].items():
            item_id = f"item_{p_data['id']}_{hit_idx}"
            tree = p_data['tree']
            if tree.exists(item_id):
                bbox = tree.bbox(item_id, column="crit_status")
                if bbox:
                    x, y, w, h = bbox
                    cb.place(x=x, y=y, width=w, height=h)
                else:
                    cb.place_forget()
            else:
                cb.place_forget()

    def on_panel_input_changed(self, p_data):
        p_data['user_hit_modes'].clear()
        self.calculate_panel(p_data)

    def on_global_input_changed(self):
        for p_data in self.panels:
            p_data['user_hit_modes'].clear()
        self.calculate_all_panels()

    def handle_item_change(self, p_data, changed_id):
        p_data['user_hit_modes'].clear()

        item_vars = p_data['item_vars']
        if changed_id == 'item4' and item_vars['item4'].get():
            item_vars['item9'].set(False)
        elif changed_id == 'item9' and item_vars['item9'].get():
            item_vars['item4'].set(False)

        selected_count = sum(1 for v in item_vars.values() if v.get())
        p_data['lbl_selected_count'].config(text=f"已選: {selected_count}/6")

        for item in ITEMS_DATA:
            item_id = item['id']
            cb = p_data['item_cb_widgets'][item_id]
            should_disable = False

            if item_id == 'item9' and item_vars['item4'].get():
                should_disable = True
            if item_id == 'item4' and item_vars['item9'].get():
                should_disable = True

            if selected_count >= 6 and not item_vars[item_id].get():
                should_disable = True

            if should_disable:
                cb.config(state="disabled")
            else:
                cb.config(state="normal")

        self.calculate_panel(p_data)

    def has_item(self, p_data, item_id):
        return p_data['item_vars'][item_id].get()

    def calculate_sim(self, p_data, fixed_mode, params):
        target_max_hp = params['target_max_hp']
        target_armor = params['target_armor']
        flat_pierce = params['flat_pierce']
        pierce_percent = params['pierce_percent']
        ad = params['ad']
        raw_chen_xing = params['raw_chen_xing']
        raw_ri_ying = params['raw_ri_ying']
        avg_crit_factor = params['avg_crit_factor']
        crit_multiplier = params['crit_multiplier']
        light_flat_raw = params['light_flat_raw']
        light_chain_raw = params['light_chain_raw']
        magic_multiplier = params['magic_multiplier']
        rune_axe_mult = params['rune_axe_mult']

        current_hp = float(target_max_hp)
        steel_stacks = 0
        hits = 0

        def calc_effective_armor(raw_armor):
            after_flat = max(0.0, raw_armor - flat_pierce)
            return max(0.0, after_flat * (1.0 - pierce_percent / 100.0))

        def get_fenrir_mult(hp):
            return 1.3 if (self.has_item(p_data, 'item6') and hp <= target_max_hp * 0.5) else 1.0

        while current_hp > 1e-6 and hits < 200:
            hits += 1

            armor_before = target_armor * (1.0 - steel_stacks * 0.06)
            eff_armor_before = calc_effective_armor(armor_before)
            armor_mult_before = 1.0 - (eff_armor_before / (eff_armor_before + 600.0))

            base_fenrir = get_fenrir_mult(current_hp)
            base_damage_mult = base_fenrir * rune_axe_mult

            factor = avg_crit_factor
            if fixed_mode == 'ALL_CRIT':
                factor = crit_multiplier
            elif fixed_mode == 'NO_CRIT':
                factor = 1.0

            base_actual = ad * factor * armor_mult_before * base_damage_mult
            current_hp = max(0.0, current_hp - base_actual)

            if self.has_item(p_data, 'item1') and steel_stacks < 4:
                steel_stacks += 1

            armor_after = target_armor * (1.0 - steel_stacks * 0.06)
            eff_armor_after = calc_effective_armor(armor_after)
            armor_mult_after = 1.0 - (eff_armor_after / (eff_armor_after + 600.0))

            dragon_actual = 0.0
            if self.has_item(p_data, 'item2') and current_hp > 0:
                dragon_actual = (current_hp * 0.08) * armor_mult_after * get_fenrir_mult(current_hp) * rune_axe_mult
                current_hp = max(0.0, current_hp - dragon_actual)

            chen_xing_actual = 0.0
            if self.has_item(p_data, 'item9') and current_hp > 0:
                chen_xing_actual = raw_chen_xing * armor_mult_after * get_fenrir_mult(current_hp) * rune_axe_mult
                current_hp = max(0.0, current_hp - chen_xing_actual)

            ri_ying_actual = 0.0
            if self.has_item(p_data, 'item10') and current_hp > 0:
                ri_ying_actual = raw_ri_ying * armor_mult_after * get_fenrir_mult(current_hp) * rune_axe_mult
                current_hp = max(0.0, current_hp - ri_ying_actual)

            lightning_actual = 0.0
            if self.has_item(p_data, 'item7') and current_hp > 0:
                raw_light = light_flat_raw + (light_chain_raw if hits % 3 == 0 else 0.0)
                lightning_actual = raw_light * magic_multiplier * get_fenrir_mult(current_hp) * rune_axe_mult
                current_hp = max(0.0, current_hp - lightning_actual)

            total_hit_dmg = base_actual + dragon_actual + chen_xing_actual + ri_ying_actual + lightning_actual
            if total_hit_dmg <= 0:
                break

        return hits

    def on_hit_mode_change(self, p_data, hit_index, val):
        p_data['user_hit_modes'][hit_index] = 'CRIT' if val == '暴擊' else 'NO_CRIT'
        self.calculate_panel(p_data)

    def calculate_all_panels(self):
        for p_data in self.panels:
            self.calculate_panel(p_data)

    def calculate_panel(self, p_data):
        raw_lvl = self.get_var_int(p_data['hero_level'])
        level = max(1, min(15, raw_lvl))
        is_ranged = (p_data['hero_type'].get() == "遠程")
        ad = float(self.get_var_int(p_data['hero_ad']))
        flat_pierce = float(self.get_var_int(p_data['flat_pierce']))

        arc_crit_rate = self.get_var_float(p_data['arcana_crit_rate'])
        arc_crit_dmg = self.get_var_float(p_data['arcana_crit_dmg'])
        has_rune_blessing = p_data['rune_blessing'].get()
        has_rune_axe = p_data['rune_axe'].get()

        rune_axe_mult = 1.03 if has_rune_axe else 1.0

        target_max_hp = float(self.get_var_int(self.var_target_hp))
        target_armor = float(self.get_var_int(self.var_target_armor))
        target_marmor = float(self.get_var_int(self.var_target_marmor))

        equip_crit_rate = 0.0
        equip_crit_dmg_percent = 0.0
        pierce_percent = 0.0

        if self.has_item(p_data, 'item3'):
            equip_crit_rate += 25.0
            equip_crit_dmg_percent += 40.0
        if self.has_item(p_data, 'item5'):
            equip_crit_rate += 25.0
        if self.has_item(p_data, 'item8'):
            equip_crit_rate += 20.0
        if self.has_item(p_data, 'item10'):
            equip_crit_rate += 10.0
        if self.has_item(p_data, 'item11'):
            equip_crit_rate += 20.0
        if self.has_item(p_data, 'item12'):
            equip_crit_rate += 10.0

        if self.has_item(p_data, 'item4'):
            pierce_percent += 35.0
        elif self.has_item(p_data, 'item9'):
            equip_crit_rate += 10.0
            pierce_percent += 40.0 if is_ranged else 20.0

        if has_rune_blessing:
            equip_crit_rate *= 1.16

        total_crit_rate = min(100.0, arc_crit_rate + equip_crit_rate)
        total_crit_dmg_percent = 200.0 + arc_crit_dmg + equip_crit_dmg_percent

        raw_chen_xing = (100.0 if is_ranged else 50.0) if self.has_item(p_data, 'item9') else 0.0
        raw_ri_ying = (100.0 if is_ranged else 50.0) if self.has_item(p_data, 'item10') else 0.0

        effective_crit_rate = max(0.0, total_crit_rate / 100.0)
        crit_multiplier = total_crit_dmg_percent / 100.0
        avg_crit_factor = 1.0 + effective_crit_rate * (crit_multiplier - 1.0)

        m_armor_red_rate = target_marmor / (target_marmor + 600.0) if target_marmor > 0 else 0.0
        magic_multiplier = 1.0 - m_armor_red_rate

        lvl_factor = (level - 1) / 14.0
        light_flat_raw = 45.0 + (87.0 - 45.0) * lvl_factor
        light_chain_raw = 150.0 + (430.0 - 150.0) * lvl_factor

        def calc_effective_armor(raw_armor):
            after_flat = max(0.0, raw_armor - flat_pierce)
            return max(0.0, after_flat * (1.0 - pierce_percent / 100.0))

        initial_eff_armor = calc_effective_armor(target_armor)
        initial_armor_red = initial_eff_armor / (initial_eff_armor + 600.0) if initial_eff_armor > 0 else 0.0

        p_data['lbl_crit_rate'].config(text=f"總暴擊率：{total_crit_rate:.1f}%")
        p_data['lbl_crit_dmg'].config(text=f"暴傷倍率：{total_crit_dmg_percent:.1f}%")
        p_data['lbl_eff_armor'].config(text=f"有效物防：{round(initial_eff_armor)}")
        p_data['lbl_armor_red'].config(text=f"物防減傷：{initial_armor_red * 100:.1f}%")

        has_crit_ability = (total_crit_rate > 0)
        if not has_crit_ability:
            p_data['calc_mode'].set("期望值計算模式")
            p_data['cb_calc_mode'].config(state="disabled")
            p_data['card_min'].pack_forget()
            p_data['card_max'].pack_forget()
            p_data['lbl_label_avg'].config(text="普攻次數")
            is_manual = False
        else:
            p_data['cb_calc_mode'].config(state="readonly")
            p_data['card_min'].pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=1)
            p_data['card_max'].pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=1)
            is_manual = ("手動控制" in p_data['calc_mode'].get())
            p_data['lbl_label_avg'].config(text="當前設定次數" if is_manual else "期望值普攻次數")

        columns = ["hit"]
        headers = ["次數"]
        if is_manual:
            columns.append("crit_status")
            headers.append("暴擊設定")
        if self.has_item(p_data, 'item1'):
            columns.append("steel")
            headers.append("鋼槍層")
        columns.append("base_dmg")
        headers.append("基礎物傷")

        if self.has_item(p_data, 'item2'):
            columns.append("dragon")
            headers.append("龍骨")
        if self.has_item(p_data, 'item9'):
            columns.append("chen_xing")
            headers.append("晨星")
        if self.has_item(p_data, 'item10'):
            columns.append("ri_ying")
            headers.append("日影")
        if self.has_item(p_data, 'item7'):
            columns.append("lightning")
            headers.append("雷電")

        columns.extend(["total_dmg", "hp_end"])
        headers.extend(["單擊總傷", "剩餘血量"])

        tree = p_data['tree']
        tree["columns"] = columns
        for col, head in zip(columns, headers):
            tree.heading(col, text=head)
            tree.column(col, width=65, anchor="center")

        for row in tree.get_children():
            tree.delete(row)

        self.clear_comboboxes(p_data)

        if target_max_hp <= 0:
            p_data['lbl_min_hits'].config(text="0 次")
            p_data['lbl_avg_hits'].config(text="0 次")
            p_data['lbl_max_hits'].config(text="0 次")
            return

        sim_params = {
            'target_max_hp': target_max_hp,
            'target_armor': target_armor,
            'flat_pierce': flat_pierce,
            'pierce_percent': pierce_percent,
            'ad': ad,
            'raw_chen_xing': raw_chen_xing,
            'raw_ri_ying': raw_ri_ying,
            'avg_crit_factor': avg_crit_factor,
            'crit_multiplier': crit_multiplier,
            'light_flat_raw': light_flat_raw,
            'light_chain_raw': light_chain_raw,
            'magic_multiplier': magic_multiplier,
            'rune_axe_mult': rune_axe_mult
        }

        if has_crit_ability:
            min_hits = self.calculate_sim(p_data, 'ALL_CRIT', sim_params)
            max_hits = self.calculate_sim(p_data, 'NO_CRIT', sim_params)
            p_data['lbl_min_hits'].config(text=f"{min_hits} 次")
            p_data['lbl_max_hits'].config(text=f"{max_hits} 次")

        current_hp = target_max_hp
        steel_stacks = 0
        hits = 0

        def get_fenrir_mult(hp):
            return 1.3 if (self.has_item(p_data, 'item6') and hp <= target_max_hp * 0.5) else 1.0

        while current_hp > 1e-6 and hits < 200:
            hits += 1

            armor_before = target_armor * (1.0 - steel_stacks * 0.06)
            eff_armor_before = calc_effective_armor(armor_before)
            armor_mult_before = 1.0 - (eff_armor_before / (eff_armor_before + 600.0))

            base_fenrir = get_fenrir_mult(current_hp)
            base_damage_mult = base_fenrir * rune_axe_mult

            factor = 1.0
            hit_mode = 'CRIT'

            if not has_crit_ability or not is_manual:
                factor = avg_crit_factor
            else:
                hit_mode = p_data['user_hit_modes'].get(hits, 'CRIT')
                factor = crit_multiplier if hit_mode == 'CRIT' else 1.0

            base_actual = ad * factor * armor_mult_before * base_damage_mult
            current_hp = max(0.0, current_hp - base_actual)

            stack_for_display = steel_stacks
            if self.has_item(p_data, 'item1') and steel_stacks < 4:
                steel_stacks += 1

            armor_after = target_armor * (1.0 - steel_stacks * 0.06)
            eff_armor_after = calc_effective_armor(armor_after)
            armor_mult_after = 1.0 - (eff_armor_after / (eff_armor_after + 600.0))

            dragon_actual = 0.0
            if self.has_item(p_data, 'item2') and current_hp > 0:
                dragon_actual = (current_hp * 0.08) * armor_mult_after * get_fenrir_mult(current_hp) * rune_axe_mult
                current_hp = max(0.0, current_hp - dragon_actual)

            chen_xing_actual = 0.0
            if self.has_item(p_data, 'item9') and current_hp > 0:
                chen_xing_actual = raw_chen_xing * armor_mult_after * get_fenrir_mult(current_hp) * rune_axe_mult
                current_hp = max(0.0, current_hp - chen_xing_actual)

            ri_ying_actual = 0.0
            if self.has_item(p_data, 'item10') and current_hp > 0:
                ri_ying_actual = raw_ri_ying * armor_mult_after * get_fenrir_mult(current_hp) * rune_axe_mult
                current_hp = max(0.0, current_hp - ri_ying_actual)

            lightning_actual = 0.0
            if self.has_item(p_data, 'item7') and current_hp > 0:
                raw_light = light_flat_raw + (light_chain_raw if hits % 3 == 0 else 0.0)
                lightning_actual = raw_light * magic_multiplier * get_fenrir_mult(current_hp) * rune_axe_mult
                current_hp = max(0.0, current_hp - lightning_actual)

            total_hit_dmg = base_actual + dragon_actual + chen_xing_actual + ri_ying_actual + lightning_actual

            if total_hit_dmg <= 0:
                break

            row_vals = [f"第 {hits} 次"]
            if is_manual:
                row_vals.append("")
            if self.has_item(p_data, 'item1'):
                row_vals.append(f"{stack_for_display}層")
            row_vals.append(f"{base_actual:.1f}")

            if self.has_item(p_data, 'item2'):
                row_vals.append(f"{dragon_actual:.1f}")
            if self.has_item(p_data, 'item9'):
                row_vals.append(f"{chen_xing_actual:.1f}")
            if self.has_item(p_data, 'item10'):
                row_vals.append(f"{ri_ying_actual:.1f}")
            if self.has_item(p_data, 'item7'):
                row_vals.append(f"{lightning_actual:.1f}")

            row_vals.extend([f"{total_hit_dmg:.1f}", f"{current_hp:.1f}"])

            item_id = f"item_{p_data['id']}_{hits}"
            tree.insert("", tk.END, iid=item_id, values=row_vals)

            if is_manual:
                cb_val = tk.StringVar(value="暴擊" if hit_mode == 'CRIT' else "未暴擊")
                cb = ttk.Combobox(tree, textvariable=cb_val, values=["暴擊", "未暴擊"], state="readonly", width=5)
                cb.bind("<<ComboboxSelected>>", lambda e, pd=p_data, idx=hits, v=cb_val: self.on_hit_mode_change(pd, idx, v.get()))
                p_data['combobox_widgets'][hits] = cb

        p_data['lbl_avg_hits'].config(text=f"{hits} 次")
        self.root.update_idletasks()
        self.update_combobox_positions(p_data)

if __name__ == "__main__":
    root = tk.Tk()
    app = AoVCalculatorApp(root)
    root.mainloop()