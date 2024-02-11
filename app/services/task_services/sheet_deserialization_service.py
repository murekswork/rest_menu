class SheetDeserializationService:

    @staticmethod
    def create_menu(row) -> dict:
        """Make menu object from sheet row"""
        return {
            'title': row[1],
            'description': row[2],
            'submenus': []
        }

    @staticmethod
    def create_submenu(row) -> dict:
        """Make submenu object from sheet row"""
        return {
            'title': row[2],
            'description': row[3],
            'dishes': []
        }

    @staticmethod
    def create_dish(row) -> dict:
        """Make a dish object from sheet row"""
        return {
            'title': row[3],
            'description': row[4],
            'price': float(row[5].replace(',', '.'))
        }

    @staticmethod
    def create_sale(row):
        """Make a sale object from sheet row"""
        return {
            'title': row[3],
            'description': row[4],
            'sale': row[6]
        }

    @classmethod
    async def create_objects_from_sheet_rows(cls,
                                             sheet_data: list[list]) -> dict:
        """
        Method iterates over each row in the sheet data and creates Menu,
        Submenu, Dish, and Sale objects based on the content of each row.
        It organizes the objects into a hierarchical structure representing the
        menu data.The created objects are stored in lists and dictionaries for
        easy access and manipulation.Finally, it returns a dictionary
        containing the parsed menus and sales data.
        """

        menus = []
        sales = []
        current_menu: dict = {}
        current_submenu: dict = {}

        for row in sheet_data:
            if row[0]:
                current_menu = cls.create_menu(row)
                menus.append(current_menu)
                current_submenu = {}
            elif row[1]:
                current_submenu = cls.create_submenu(row)
                current_menu['submenus'].append(current_submenu)
            elif row[2]:
                dish = cls.create_dish(row)
                current_submenu['dishes'].append(dish)
            if row[6]:
                sale = cls.create_sale(row)
                sales.append(sale)

        return {'menus': menus, 'sales': sales}
