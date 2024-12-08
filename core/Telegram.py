import telebot, time
from telebot import types
from sql_mg import SQL



class Bot:
    def __init__(self, token, host_db, user_db, pass_db, db_):

        # bot init
        self.token = token
        self.bot = telebot.TeleBot(self.token)
        # admin
        self.admin_ids = (3333, 2222, 1111)
        # sql init
        self.sql = SQL(host_db, user_db, pass_db, db_)
        # user_data
        self.user_data = {}
        self.demand_data = {}
        self.supply_data = {}
        self.view_data = {}
        self.requests_list = []
        # auth menu
        auth_button = types.KeyboardButton('احراز هویت')

        self.auth_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        self.auth_menu.row(auth_button)

        # request menu
        demand_register = types.KeyboardButton('درخواست تقاضا')
        supply_register = types.KeyboardButton('ثبت عرضه')
        main_menu = types.KeyboardButton('منو اصلی')
        self.request_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        self.request_menu.row(supply_register, demand_register)
        self.request_menu.row(main_menu)

        # admin menu
        list_of_new_users = types.KeyboardButton('نمایش کاربران جدید')
        checklist_of_pairs = types.KeyboardButton('لیست درخواست ها')

        admin_show_supplys = types.KeyboardButton('لیست عرضه ها/تقاضاها')

        self.admin_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        self.admin_menu.row(list_of_new_users, checklist_of_pairs)
        self.admin_menu.row(admin_show_supplys)
        # client menu
        requests_register = types.KeyboardButton('ثبت درخواست')
        show_requests = types.KeyboardButton('مشاهده درخواست ها')
        self.client_menu = types.ReplyKeyboardMarkup(resize_keyboard=True ,row_width=2)
        self.client_menu.row(requests_register,show_requests)

        # self made funcs
        def format_price(number):
            if number is None:
                return "N/A"

            try:
                number = float(
                    str(number).replace(",", ""))
                return "{:,.0f}".format(number)

            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid number: {number}") from e

        def get_address(message):
            user_id = message.chat.id
            address = message.text
            self.demand_data[user_id]['address'] = address
            demand_info = self.demand_data[user_id]
            print(format_price(demand_info['price']))
            formated_shape = demand_info['price']
            formated_shape_test = format_price(formated_shape)
            confirmation_text = (
                "اطلاعات وارد شده:\n"
                f"نوع درخواست: {demand_info['demand_type']}\n"
                f"تعداد کل طبقات: {demand_info['total_floors']}\n"
                f"تعداد طبقات زیر زمین: {demand_info['underground_floors']}\n"
                f"مساحت سطح اشغال: {demand_info['surface_area']}\n"
                f"کل زیر بنا: {demand_info['building_area']}\n"
                f"مکان: {demand_info['location']}\n"
                f"قیمت پیشنهادی: {formated_shape_test}\n"
                f"آدرس: {demand_info['address']}"
            )

            confirm_button = types.InlineKeyboardButton('تایید', callback_data='confirm_demand')
            reject_button = types.InlineKeyboardButton('عدم تایید', callback_data='reject_demand')
            inline_menu = types.InlineKeyboardMarkup()
            inline_menu.row(confirm_button, reject_button)

            self.bot.send_message(user_id, f'{confirmation_text}\n\n آیا درخواست مورد تایید است؟',
                                  reply_markup=inline_menu)

        def get_price(message):
            user_id = message.chat.id
            price = message.text

            self.demand_data[user_id]['price'] = price

            self.bot.send_message(user_id, 'آدرس تقریبی پروژه را وارد کنید:')
            self.bot.register_next_step_handler(message, get_address)

        def get_location(call):
            print(f"Entering get_location for user: {call.message.chat.id}")
            user_id = call.message.chat.id
            self.bot.send_message(user_id, 'قیمت پیشنهادی را وارد کنید:(فقط عدد و به تومان باشد)')
            self.bot.register_next_step_handler(call.message, get_price)

        def get_building_area(message):
            user_id = message.chat.id
            building_area = message.text
            self.demand_data[user_id]['building_area'] = building_area
            
            inline_menu = types.InlineKeyboardMarkup()
            tehran = types.InlineKeyboardButton('تهران', callback_data='c:تهران')
            county = types.InlineKeyboardButton('شهرستان', callback_data='c:شهرستان')
            inline_menu.add(tehran, county)
            self.bot.send_message(user_id, 'آیا پروژه در تهران است یا شهرستان؟', reply_markup=inline_menu)

        def get_surface_area(message):
            user_id = message.chat.id
            surface_area = message.text
            self.demand_data[user_id]['surface_area'] = surface_area

            self.bot.send_message(user_id, 'کل زیر بنا را وارد کنید:')
            self.bot.register_next_step_handler(message, get_building_area)

        def get_underground_floors(message):
            user_id = message.chat.id
            underground_floors = message.text
            self.demand_data[user_id]['underground_floors'] = underground_floors

            self.bot.send_message(user_id, 'مساحت سطح اشغال را وارد کنید:')
            self.bot.register_next_step_handler(message, get_surface_area)

        def get_total_floors(message):
            user_id = message.chat.id
            total_floors = message.text
            self.demand_data[user_id]['total_floors'] = total_floors

            self.bot.send_message(user_id, 'تعداد طبقات زیر زمین را وارد کنید:')
            self.bot.register_next_step_handler(message, get_underground_floors)

        def demand_handler(call):
            user_id = call.message.chat.id
            demand_type = call.data.split(':')[1]
            self.user_data[user_id] = {}
            self.demand_data[user_id]['demand_type'] = demand_type

            self.bot.send_message(user_id, 'تعداد کل طبقات را وارد کنید:')
            self.bot.register_next_step_handler(call.message, get_total_floors)

        def get_license_number(message):
            print(message.text)
            chat_id = message.chat.id
            self.user_data[chat_id]['license_number'] = message.text

            supplier = types.InlineKeyboardButton('عرضه کننده', callback_data=f'type:supplier')
            demander = types.InlineKeyboardButton('متقاضی', callback_data=f'type:demander')
            both = types.InlineKeyboardButton('هردو', callback_data=f'type:both')

            type_menu = types.InlineKeyboardMarkup(row_width=2)
            type_menu.row(supplier, demander)
            type_menu.row(both)

            self.bot.send_message(chat_id, "لطفا نوع کاربری خود را انتخاب کنید:", reply_markup=type_menu)

        def get_company_name(message):
            print(message.text)
            chat_id = message.chat.id
            self.user_data[chat_id]['company_name'] = message.text
            self.bot.send_message(chat_id, "لطفا شماره پروانه خود را وارد کنید:")
            self.bot.register_next_step_handler(message, get_license_number)

        def get_last_name(message):
            print(message.text)
            chat_id = message.chat.id
            self.user_data[chat_id]['last_name'] = message.text
            self.bot.send_message(chat_id, "نام شرکت خود را وارد کنید:")
            self.bot.register_next_step_handler(message, get_company_name)

        def get_first_name(message):
            print(message.text)
            chat_id = message.chat.id
            self.user_data[chat_id]['first_name'] = message.text
            self.bot.send_message(chat_id, "لطفا نام خانوادگی خود را وارد کنید:")
            self.bot.register_next_step_handler(message, get_last_name)

        def get_phone_number(message):
            user_id = message.chat.id


            if message.text.startswith('09') and len(message.text) == 11:
                print("1")
                self.user_data[user_id] = {}
                self.user_data[user_id]['phone_number'] = message.text
                self.bot.send_message(user_id, "لطفا نام خود را وارد کنید:")
                self.bot.register_next_step_handler(message, get_first_name)
            else:
                self.bot.send_message(chat_id=user_id,
                                      text="شماره وارد شده معتبر نیست. لطفا شماره‌ای که با 09 شروع می‌شود و 11 رقمی است وارد کنید.")
                self.bot.register_next_step_handler(message, get_phone_number)

        # client check
        def check_client(func):
            def wrapper(*args, **kwargs):
                message = args[0]
                user_id = message.chat.id
                auth_status = self.sql.check_user_auth_status(user_id)

                if auth_status == 'approved':
                    return func(*args, **kwargs)
                elif auth_status == 'rejected':
                    self.bot.send_message(chat_id=user_id, text="شما دسترسی ندارید.")
                    return None
                else:
                    self.bot.send_message(chat_id=user_id, text="منتظر تایید احراز هویت بمانید.")


            return wrapper


        # start button
        @self.bot.message_handler(commands=['start'])
        def start(message):
            user_id = message.chat.id
            print(message.text)
            fname = message.from_user.first_name
            user_exist = self.sql.check_user_auth(user_id)

            if user_exist:
                self.bot.send_message(chat_id=user_id,
                                      text=f'خوش آمدید {fname}!')
                user_info = (f'ID: {user_exist[0]}\nPhone: {user_exist[1]}\nStatus: {user_exist[2]}\n'
                             f'First Name: {user_exist[4]}\nLast Name: {user_exist[5]}\nCompany: {user_exist[6]}\n'
                             f'licensse: {user_exist[7]}\nuser type: {user_exist[8]}')
                self.bot.send_message(chat_id=user_id, text=user_info, reply_markup=self.client_menu)

            else:
                self.bot.send_message(chat_id=user_id,
                                      text=f'خوش آمدید {fname}!\nشما کاربر جدید هستید لطفا احراز هویت کنید', reply_markup=self.auth_menu)

        @self.bot.message_handler(func=lambda message: message.text == "منو اصلی")
        @check_client
        def home_menu(message):
            user_id = message.chat.id
            self.bot.send_message(user_id,  'منو اصلی:', reply_markup=self.client_menu)

        @self.bot.message_handler(func=lambda message: message.text == "ثبت عرضه")
        @check_client
        def supply_offer(message):
            user_id = message.chat.id
            self.supply_data[user_id] = {}

            inline_menu = types.InlineKeyboardMarkup()
            soil = types.InlineKeyboardButton('خاک', callback_data='offer:خاک')
            concrete = types.InlineKeyboardButton('بتن', callback_data='offer:بتن')
            boil = types.InlineKeyboardButton('جوش', callback_data='offer:جوش')
            inline_menu.add(soil, concrete, boil)

            self.bot.send_message(user_id, 'نوع ماده را انتخاب کنید:', reply_markup=inline_menu)

        @self.bot.message_handler(func=lambda message: message.text == "درخواست تقاضا")
        @check_client
        def supply_register(message):
            print(message.text)
            user_id = message.chat.id
            self.demand_data[user_id] = {}
            # inline menu
            soil = types.InlineKeyboardButton('خاک', callback_data=f'demand:خاک')
            concrete = types.InlineKeyboardButton('بتن', callback_data=f'demand:بتن')
            boil = types.InlineKeyboardButton('جوش', callback_data=f'demand:جوش')

            inline_menu = types.InlineKeyboardMarkup()
            inline_menu.row(soil, concrete, boil)
            self.bot.send_message(user_id, 'درخواست خاک-بتن-جوش:', reply_markup=inline_menu)

        @self.bot.message_handler(func=lambda message: message.text == "ثبت درخواست")
        @check_client
        def set_request(message):
            print(message.text)
            user_id = message.chat.id
            self.bot.send_message(user_id, 'درخواست عرضه یا تقاضا؟', reply_markup=self.request_menu)



        @self.bot.message_handler(func=lambda message: message.text == "مشاهده درخواست ها")
        @check_client
        def view_requests(message):
            user_id = message.chat.id
            self.view_data[user_id] = {}
            inline_menu = types.InlineKeyboardMarkup()
            supply = types.InlineKeyboardButton('عرضه', callback_data='filter:offers')
            demand = types.InlineKeyboardButton('تقاضا', callback_data='filter:demands')
            inline_menu.add(supply, demand)
            self.bot.send_message(user_id, 'لطفاً نوع درخواست را انتخاب کنید:', reply_markup=inline_menu)

        @self.bot.message_handler(func=lambda message: message.text == "احراز هویت")
        def auth_(message):
            user_id = message.chat.id

            user_exist = self.sql.check_user_auth(user_id)
            if user_exist:
                self.bot.send_message(chat_id=user_id, text="شما قبلاً ثبت‌نام کرده‌اید.")
            else:
                self.bot.send_message(chat_id=user_id,
                                      text='\nشماره خود را وارد نمایید (شماره وارد شده باید با 09 شروع شود و باید شماره با کیبورد انگلیسی وارد شود)'
                                           'لطفا مراحل احراز هویت را تا اخر و کامل طی فرمایید.',
                                      reply_markup=self.auth_menu)
                self.bot.register_next_step_handler(message, get_phone_number)


        # admin
        def check_admin(func):
            def wrapper(*args, **kwargs):
                message = args[0]
                user_id = message.chat.id
                if user_id == 789630889 or user_id in self.admin_ids:
                    return func(*args, **kwargs)
                else:
                    self.bot.send_message(chat_id=user_id, text="شما دسترسی ادمین ندارید.")
                    return None

            return wrapper

        @self.bot.message_handler(commands=['admin'])
        @check_admin
        def main_admin(message):
            user_id = message.chat.id

            self.bot.send_message(user_id,f'به منو ادمین خوش امدید{message.from_user.first_name}!', reply_markup=self.admin_menu)

        @self.bot.message_handler(func=lambda message: message.text == "لیست عرضه ها/تقاضاها")
        @check_admin
        def view_requests_admin(message):
            user_id = message.chat.id
            self.view_data[user_id] = {}
            inline_menu = types.InlineKeyboardMarkup()
            supply = types.InlineKeyboardButton('عرضه', callback_data='filter:offers')
            demand = types.InlineKeyboardButton('تقاضا', callback_data='filter:demands')
            inline_menu.add(supply, demand)
            self.bot.send_message(user_id, 'لطفاً نوع درخواست را انتخاب کنید:', reply_markup=inline_menu)
        

        @self.bot.message_handler(func=lambda message: message.text == "لیست درخواست ها")
        @check_admin
        def list_of_requests(message):
            admin_id = message.chat.id
            if not self.requests_list:
                self.bot.send_message(admin_id, "هیچ درخواستی ثبت نشده است.")
                return

            for request, request_id, type in self.requests_list:
                if type == 'demand':
                    markup = types.InlineKeyboardMarkup()
                    print('numberid', request_id, type)
                    view_button = types.InlineKeyboardButton('حذف', callback_data=f"dd:{request_id}:359")
                    markup.add(view_button)
                    self.bot.send_message(admin_id, request, reply_markup=markup)
                else:
                    markup = types.InlineKeyboardMarkup()
                    print('numberid', request_id, type)
                    view_button = types.InlineKeyboardButton('حذف', callback_data=f"dy:{request_id}:359")
                    markup.add(view_button)
                    self.bot.send_message(admin_id, request, reply_markup=markup)




        @self.bot.message_handler(func=lambda message: message.text == "نمایش کاربران جدید")
        @check_admin
        def show_new_users(message):
            print(message.text)
            userid = message.chat.id
            results = self.sql.show_all_new_users()
            phone_status_cache = {}

            if results:
                for result in results:
                    print(message.text)
                    print(result)
                    client_user_id, phone_number, first_name, last_name, company_name, license_number, user_type = result

                    # Check if the phone number has already been checked
                    if phone_number in phone_status_cache:
                        auth_status = phone_status_cache[phone_number]
                        print(auth_status)
                    else:
                        auth_status = self.sql.check_phone_duplicate(phone_number)
                        phone_status_cache[phone_number] = auth_status  # Cache the result
                        print(auth_status)
                    user_info = (f'ID: {client_user_id}\nPhone: {phone_number}\n'
                                 f'First Name: {first_name}\nLast Name: {last_name}\nCompany: {company_name}\n'
                                 f'License: {license_number}\nUser Type: {user_type}\n')
                    if auth_status[0] == 'approved':
                        user_info += 'این شماره قبلاً ثبت شده و تایید شده است.'
                    elif auth_status[0] == 'rejected':
                        user_info += 'این شماره قبلاً ثبت شده و رد شده است.'
                    elif auth_status[0] == 'pending':
                        user_info += 'این شماره قبلاً ثبت شده و در حال انتظار است.'

                    # Inline menu
                    approve = types.InlineKeyboardButton('تایید', callback_data=f'approved:{client_user_id}')
                    reject = types.InlineKeyboardButton('رد', callback_data=f'rejected:{client_user_id}')
                    app_rej_menu = types.InlineKeyboardMarkup(row_width=2)
                    app_rej_menu.row(approve, reject)

                    self.bot.send_message(userid, user_info, reply_markup=app_rej_menu)

            else:
                self.bot.send_message(userid, "هیچ مورد جدیدی موجود نیست.")

        # callback
        @self.bot.callback_query_handler(func=lambda call: True)
        def service_handler(call):
            user_id = call.message.chat.id
            if 'type:' in call.data:
                print(call.message.text)
                user_type = call.data.split(":")[1]
                self.user_data[user_id]['user_type'] = user_type

                self.bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text="اطلاعات شما ثبت شد.")
                self.sql.insert_into_auth_table(user_id, self.user_data[user_id]['phone_number'],self.user_data[user_id]['first_name'],
                                                self.user_data[user_id]['last_name'], self.user_data[user_id]['company_name'],
                                                self.user_data[user_id]['license_number'], self.user_data[user_id]['user_type'])
                for x in self.admin_ids:
                    self.bot.send_message(chat_id=x, text='شما درخواست احراز هویت جدید داربد')

            elif 'approved' in call.data:
                client_user_id = call.data.split(":")[1]
                self.sql.accept(client_user_id)
                self.bot.send_message(client_user_id, 'درخواست احراز هویت شما مورد تایید قرار گرفت.',
                                      reply_markup=self.client_menu)
                try:
                    self.bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
                    self.bot.send_message(chat_id=user_id, text="done!")
                except telebot.apihelper.ApiTelegramException as e:
                    print(f"Error occurred: {e}")

            elif 'rejected' in call.data:
                client_user_id = call.data.split(":")[1]
                self.sql.reject(client_user_id)
                self.bot.send_message(client_user_id, 'درخواست احراز هویت شما رد شد.')
                try:
                    self.bot.delete_message(chat_id=user_id, message_id=call.message.message_id)

                    self.bot.send_message(chat_id=user_id, text="done!")

                except telebot.apihelper.ApiTelegramException as e:
                    print(f"Error occurred: {e}")

            elif 'demand:' in call.data:
                self.bot.delete_message(chat_id=user_id, message_id=call.message.message_id)

                demand_handler(call)

            elif call.data == 'confirm_demand':
                self.bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
                demand_info = self.demand_data[user_id]
                self.sql.insert_into_demand_table(
                    user_id=user_id,
                    material_type=demand_info['demand_type'],
                    total_floors=demand_info['total_floors'],
                    underground_floors=demand_info['underground_floors'],
                    surface_area=demand_info['surface_area'],
                    total_building_area=demand_info['building_area'],
                    location=demand_info['location'],
                    proposed_price=demand_info['price'],
                    approximate_address=demand_info['address']
                )

                self.bot.send_message(user_id, 'درخواست شما با موفقیت ثبت شد.', reply_markup=self.client_menu)

            elif call.data == 'reject_demand':
                self.bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
                self.bot.send_message(user_id, 'لطفاً اطلاعات خود را مجدداً وارد کنید.')
                del self.demand_data[user_id]

            if 'offer:' in call.data:
                self.bot.delete_message(chat_id=user_id, message_id=call.message.message_id)

                material_type = call.data.split(":")[1]

                self.supply_data[user_id]['material_type'] = material_type
                inline_menu = types.InlineKeyboardMarkup()

                level_one = types.InlineKeyboardButton('یک', callback_data='license_level:یک')

                level_two = types.InlineKeyboardButton('دو', callback_data='license_level:دو')

                level_three = types.InlineKeyboardButton('سه', callback_data='license_level:سه')

                inline_menu.add(level_one, level_two, level_three)

                self.bot.send_message(user_id, 'سطح پروانه را انتخاب کنید:', reply_markup=inline_menu)

            elif 'license_level:' in call.data:
                user_id = call.message.chat.id
                self.bot.delete_message(chat_id=user_id, message_id=call.message.message_id)

                license_level = call.data.split(":")[1]
                self.supply_data[user_id]['license_level'] = license_level

                inline_menu = types.InlineKeyboardMarkup()

                tehran = types.InlineKeyboardButton('تهران', callback_data='location:تهران')

                county = types.InlineKeyboardButton('شهرستان', callback_data='location:شهرستان')

                inline_menu.add(tehran, county)

                self.bot.send_message(user_id, 'مکان را انتخاب کنید:', reply_markup=inline_menu)

            elif 'location:' in call.data:

                self.bot.delete_message(chat_id=user_id, message_id=call.message.message_id)

                location = call.data.split(":")[1]

                self.supply_data[user_id]['location'] = location

                offer_info = self.supply_data[user_id]

                confirmation_text = f"""
                اطلاعات وارد شده:
               نوع ماده: {offer_info['material_type']}
               سطح پروانه: {offer_info['license_level']}
               مکان: {offer_info['location']}
                """

                markup = types.InlineKeyboardMarkup()

                approve_button = types.InlineKeyboardButton("تأیید", callback_data=f"approve:{user_id}")

                reject_button = types.InlineKeyboardButton("رد", callback_data=f"reject:{user_id}")

                markup.add(approve_button, reject_button)

                self.bot.send_message(user_id, f'{confirmation_text}\n\n آیا درخواست مورد تایید است؟',
                                      reply_markup=markup)


            elif "approve:" in call.data:
                self.bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
                user_id = int(call.data.split(":")[1])
                print(f"User ID type: {type(user_id)}, User ID: {user_id}")
                self.sql.insert_into_offers(user_id, self.supply_data[user_id]['material_type'],
                                            self.supply_data[user_id]['license_level'],
                                            self.supply_data[user_id]['location'])
                self.bot.send_message(user_id, "درخواست شما تأیید شد.", reply_markup=self.client_menu)


            elif "reject:" in call.data:
                self.bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
                user_id = call.data.split(":")[1]

                self.bot.send_message(user_id, "درخواست شما رد شد.", reply_markup=self.client_menu)

                del self.supply_data[user_id]
            elif 'filter:' in call.data:

                self.bot.delete_message(chat_id=user_id, message_id=call.message.message_id)

                filter_type = call.data.split(":")[1]
                self.view_data[user_id]['type'] = filter_type

                inline_menu = types.InlineKeyboardMarkup()
                soil = types.InlineKeyboardButton('خاک', callback_data='material:خاک')
                concrete = types.InlineKeyboardButton('بتن', callback_data='material:بتن')
                weld = types.InlineKeyboardButton('جوش', callback_data='material:جوش')
                inline_menu.add(soil, concrete, weld)

                self.bot.send_message(user_id, 'لطفاً نوع ماده را انتخاب کنید:', reply_markup=inline_menu)
            elif 'material:' in call.data:

                self.bot.delete_message(chat_id=user_id, message_id=call.message.message_id)

                material_type = call.data.split(":")[1]
                self.view_data[user_id]['material_type'] = material_type

                inline_menu = types.InlineKeyboardMarkup()
                tehran = types.InlineKeyboardButton('تهران', callback_data='l:تهران')
                county = types.InlineKeyboardButton('شهرستان', callback_data='l:شهرستان')
                inline_menu.add(tehran, county)
                self.bot.send_message(user_id, 'لطفاً مکان را انتخاب کنید:', reply_markup=inline_menu)
            elif 'c:' in call.data:
                user_id = call.message.chat.id
                print(f"user_id: {user_id}, call.data: {call.data}")
                self.bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
                location = call.data.split(":")[1]
                print(f"Location extracted: {location}")
                self.demand_data[user_id]['location'] = location
                print(f"Demand data updated: {self.demand_data[user_id]}")
                get_location(call)
                print("register_next_step_handler called")
            elif 'l:' in call.data:
                self.bot.delete_message(chat_id=user_id, message_id=call.message.message_id)

                location_filter = call.data.split(":")[1]
                self.view_data[user_id]['location_filter'] = location_filter

                request_type = self.view_data[user_id]['type']
                material_type = self.view_data[user_id]['material_type']
                location = self.view_data[user_id]['location_filter']


                filtered_requests = self.sql.get_filtered_requests(request_type, material_type, location)
                if user_id in self.admin_ids:
                    if filtered_requests:
                        if request_type == 'offers':
                            for offer_tuple in filtered_requests:
                                for i in range(10):
                                    print(offer_tuple[i],end='\n')
                                text = (
                                    "درخواست عرضه:\n\n"
                                    f"کاربر: {offer_tuple[1]}\n"
                                    f"نوع درخواست: {offer_tuple[2]}\n"
                                    f"پایه پروانه: {offer_tuple[3]}\n"
                                    f"مکان: {offer_tuple[4]}\n"
                                    f"تاریخ ایجاد: {offer_tuple[5].strftime('%Y-%m-%d %H:%M:%S')}\n"
                                    "\n"
                                    "اطلاعات کاربر:\n"
                                    f"نام: {offer_tuple[6]}\n"
                                    f"نام خانوادگی: {offer_tuple[7]}\n"
                                    f"شماره تلفن: {offer_tuple[8]}\n"
                                    f"نام شرکت: {offer_tuple[9]}\n"
                                )

                                markup = types.InlineKeyboardMarkup()
                                print('numberid',offer_tuple[0])
                                view_button = types.InlineKeyboardButton('حذف', callback_data=f"dy:{offer_tuple[0]}:1")
                                markup.add(view_button)
                                self.bot.send_message(user_id, text, reply_markup=markup)
                        else:
                            for demand_tuple in filtered_requests:
                                formated_shape = demand_tuple[8]
                                formated_shape_test = format_price(formated_shape)
                                print(formated_shape_test)
                                text = (
                                    "درخواست تقاضا:\n\n"
                                    f"کاربر: {demand_tuple[1]}\n"
                                    f"نوع درخواست: {demand_tuple[2]}\n"
                                    f"تعداد طبقات: {demand_tuple[3]}\n"
                                    f"تعداد طبقات زیرزمین: {demand_tuple[4]}\n"
                                    f"مساحت زمین: {demand_tuple[5]} مترمربع\n"
                                    f"مساحت زیربنا: {demand_tuple[6]} مترمربع\n"
                                    f"مکان: {demand_tuple[7]}\n"
                                    f"قیمت پیشنهادی: {formated_shape_test} تومان\n"
                                    f"آدرس تقریبی: {demand_tuple[9]}\n"
                                    f"تاریخ ایجاد: {demand_tuple[10].strftime('%Y-%m-%d %H:%M:%S')}\n"
                                    "\n"
                                    "اطلاعات کاربر:\n"
                                    f"نام: {demand_tuple[11]}\n"
                                    f"نام خانوادگی: {demand_tuple[12]}\n"
                                    f"شماره تلفن: {demand_tuple[13]}\n"
                                    f"نام شرکت: {demand_tuple[14]}\n"
                                )

                                markup = types.InlineKeyboardMarkup()
                                view_button = types.InlineKeyboardButton('حذف', callback_data=f"dd:{demand_tuple[0]}:1")
                                markup.add(view_button)
                                self.bot.send_message(user_id, text, reply_markup=markup)

                    else:
                        self.bot.send_message(call.message.chat.id, "هیچ عرضه/تقاضایی پیدا نشد.")
                else:
                    if filtered_requests:
                        if request_type == 'offers':
                            for offer_tuple in filtered_requests:
                                text = (
                                    "درخواست عرضه:\n\n"
                                    f"نوع درخواست: {offer_tuple[2]}\n"
                                    f"پایه پروانه: {offer_tuple[3]}\n"
                                    f"مکان: {offer_tuple[4]}\n"
                                    f"تاریخ ایجاد: {offer_tuple[5].strftime('%Y-%m-%d %H:%M:%S')}\n"
                                    "\n"
                                )

                                markup = types.InlineKeyboardMarkup()
                                view_button = types.InlineKeyboardButton('انتخاب',
                                                                         callback_data=f"sy:{offer_tuple[0]}")
                                markup.add(view_button)
                                self.bot.send_message(user_id, text, reply_markup=markup)
                        else:
                            for demand_tuple in filtered_requests:
                                formated_shape = demand_tuple[8]
                                formated_shape_test = format_price(formated_shape)
                                text = (
                                    "درخواست تقاضا:\n\n"
                                    f"نوع درخواست: {demand_tuple[2]}\n"
                                    f"تعداد طبقات: {demand_tuple[3]}\n"
                                    f"تعداد طبقات زیرزمین: {demand_tuple[4]}\n"
                                    f"مساحت زمین: {demand_tuple[5]} مترمربع\n"
                                    f"مساحت زیربنا: {demand_tuple[6]} مترمربع\n"
                                    f"مکان: {demand_tuple[7]}\n"
                                    f"قیمت پیشنهادی: {formated_shape_test} تومان\n"
                                    f"آدرس تقریبی: {demand_tuple[9]}\n"
                                    f"تاریخ ایجاد: {demand_tuple[10].strftime('%Y-%m-%d %H:%M:%S')}\n"
                                    "\n"

                                )

                                markup = types.InlineKeyboardMarkup()
                                view_button = types.InlineKeyboardButton('انتخاب',
                                                                         callback_data=f"sd:{demand_tuple[0]}")
                                markup.add(view_button)
                                self.bot.send_message(user_id, text, reply_markup=markup)

                    else:
                        self.bot.send_message(call.message.chat.id, "هیچ عرضه/تقاضایی پیدا نشد.")

            elif "dd:" in call.data:
                selected_massage_id = call.data.split(':')[1]

                if call.data.split(":")[2] == '359':
                    for item in self.requests_list:
                        if item[1] == selected_massage_id:
                            print(item)
                            self.requests_list.remove(item)
                            break
                self.sql.delete_requests(selected_massage_id, 'demands')
                self.bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text="done!.")

            elif "dy:" in call.data:
                selected_massage_id = call.data.split(':')[1]

                if call.data.split(":")[2] == '359':
                    for item in self.requests_list:
                        if item[1] == selected_massage_id:
                            print(item)
                            self.requests_list.remove(item)
                            break
                self.sql.delete_requests(selected_massage_id, 'offers')
                self.bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text="done!.")

            elif "sy:" in call.data:
                selected_offer_id = call.data.split(':')[1]
                self.bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                                           text="انتخاب شما با موفقیت ثبت شد و ادمین مطلع شد.")

                offer_details = self.sql.get_offer_details_offer(selected_offer_id)
                user_id_offer = offer_details[1]

                data = self.sql.check_user_auth(user_id_offer)
                data_user = self.sql.check_user_auth(user_id)

                self.bot.send_message(chat_id=user_id_offer,
                                      text="درخواست شما انتخاب شد توسط یک کاربر منتظر تماس کارشناسان ما باشید.")

                self.admin_text = (
                    f" کاربر درخواست عرضه {selected_offer_id}را انتخاب کرد.\n"
                    f"اطلاعات کاربری که درخواست داده:\n"
                    f"نام: {data_user[4]} {data_user[5]}\n"  # Assuming first_name, last_name
                    f"شماره تلفن: {data_user[1]}\n"  # Assuming phone_number
                    f"نام شرکت: {data_user[6]}\n"  # Assuming company_name
                    "\n"
                    f"اطلاعات کاربری که انتخاب کرده:\n"
                    f"نام: {data[4]} {data[5]}\n"  # Assuming first_name, last_name
                    f"شماره تلفن: {data[1]}\n"  # Assuming phone_number
                    "\n"
                    f"نوع درخواست: {offer_details[2]}\n"
                    f"پایه پروانه: {offer_details[3]}\n"
                    f"مکان: {offer_details[4]}\n"
                    f"تاریخ ایجاد: {offer_details[5].strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                self.requests_list.append((self.admin_text, selected_offer_id, 'offer'))

            elif "sd:" in call.data:
                selected_demand_id = call.data.split(':')[1]
                self.bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                                           text="انتخاب شما با موفقیت ثبت شد و ادمین مطلع شد.")
                demand_details = self.sql.get_offer_details_demand(selected_demand_id)
                user_id_demand = demand_details[1]

                data = self.sql.check_user_auth(user_id_demand)
                data_user = self.sql.check_user_auth(user_id)

                self.bot.send_message(chat_id=user_id_demand, text="درخواست شما انتخاب شد توسط یک کاربر منتظر تماس کارشناسان ما باشید.")
                self.admin_text = (
                    f" کاربر درخواست تقاضا {selected_demand_id}را انتخاب کرد.\n"
                    f"اطلاعات کاربری که درخواست داده:\n"
                    f"نام: {data_user[4]} {data_user[5]}\n"  # Assuming first_name, last_name
                    f"شماره تلفن: {data_user[1]}\n"  # Assuming phone_number
                    f"نام شرکت: {data_user[6]}\n"  # Assuming company_name
                    "\n"
                    f"اطلاعات کاربری که انتخاب کرده:\n"
                    f"نام: {data[4]} {data[5]}\n"  # Assuming first_name, last_name
                    f"شماره تلفن: {data[1]}\n"  # Assuming phone_number
                    "\n"
                    f"نوع درخواست: {demand_details[2]}\n"
                    f"مکان: {demand_details[7]}\n"
                    f"تاریخ ایجاد: {demand_details[10].strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                self.requests_list.append((self.admin_text, selected_demand_id, 'demand'))


finance_bot = Bot('bottoken','localhost', 'root','pass', 'finance_bot')
while(True):

    try:
        finance_bot.bot.polling(non_stop=True)
    except Exception as ec:

        print(ec)
        time.sleep(2)
        finance_bot.bot.polling(non_stop=True)

