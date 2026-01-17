# --- Выбор устройства (клик по 1..5) ---
@router.callback_query(F.data.startswith("devsel:"))
async def select_devices(call: CallbackQuery):
    tg_id = call.from_user.id
    selected = int(call.data.split(":")[1])
    user_device_choice[tg_id] = selected

    # Перерисовываем клавиатуру с учётом выбранного
    await call.message.edit_reply_markup(
        reply_markup=kb.device_keyboard(selected)
    )
    await call.answer()

# --- Продолжить ---
@router.callback_query(F.data == "dev_continue")
async def continue_after_selection(call: CallbackQuery):
    tg_id = call.from_user.id
    selected = user_device_choice.get(tg_id, 1)

    await call.answer(f"Вы выбрали {selected} устройств", show_alert=True)
    await call.message.delete()

# --- Назад ---
@router.callback_query(F.data == "dev_back")
async def back_from_devices(call: CallbackQuery):
    await call.message.delete()
    await call.answer()


# Тариф 1 месяц
@router.callback_query(F.data == '1 месяц')
async def one_month(callback: CallbackQuery):
    await callback.answer('1 месяц')

    photo_path = "./assets/1month_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
              "💎 <b>Тариф: 1 месяц</b>\n"
              "<blockquote>─────────────────────────────────\n"
              "│ 🔖 <b>Описание:</b> Старт для начинающего интернет-воина\n"
              "│ 🗓  <b>Кол-во Дней:</b> 30\n"
              "│ 🌐 <b>Трафик:</b> ∞ Безлимит\n"
              "│ 💶 <b>Стоимость:</b> 139₽\n"
              "─────────────────────────────────</blockquote>\n\n"
              "<i>Для продолжения нажмите кнопку ниже</i> 👇"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.continue_to_choose_devices
    )

# Тариф 3 месяца
@router.callback_query(F.data == '3 месяца')
async def one_month(callback: CallbackQuery):
    await callback.answer('3 месяца')

    photo_path = "./assets/3month_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
              "💎 <b>Тариф: 3 месяца</b>\n"
              "<blockquote>─────────────────────────────────\n"
              "│ 🔖 <b>Описание:</b> Отличное сезонное решение\n"
              "│ 🗓  <b>Кол-во Дней:</b> 90\n"
              "│ 🌐 <b>Трафик:</b> ∞ Безлимит\n"
              "│ 💶 <b>Стоимость:</b> 389₽\n"
              "─────────────────────────────────</blockquote>\n\n"
              "<i>Для продолжения нажмите кнопку ниже</i> 👇"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.continue_to_choose_devices
    )

# Тариф 6 месяцев
@router.callback_query(F.data == '6 месяцев')
async def one_month(callback: CallbackQuery):
    await callback.answer('6 месяцев')

    photo_path = "./assets/6month_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
              "💎 <b>Тариф: 6 месяцев</b>\n"
              "<blockquote>─────────────────────────────────\n"
              "│ 🔖 <b>Описание:</b> Полгода наслаждения быстрым VPN\n"
              "│ 🗓  <b>Кол-во Дней:</b> 180\n"
              "│ 🌐 <b>Трафик:</b> ∞ Безлимит\n"
              "│ 💶 <b>Стоимость:</b> 749₽\n"
              "─────────────────────────────────</blockquote>\n\n"
              "<i>Для продолжения нажмите кнопку ниже</i> 👇"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.continue_to_choose_devices
    )

# Тариф 9 месяцев
@router.callback_query(F.data == '9 месяцев')
async def one_month(callback: CallbackQuery):
    await callback.answer('9 месяцев')

    photo_path = "./assets/9month_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
              "💎 <b>Тариф: 9 месяцев</b>\n"
              "<blockquote>─────────────────────────────────\n"
              "│ 🔖 <b>Описание:</b> Стойкий запах 50 миллионов мощи\n"
              "│ 🗓  <b>Кол-во Дней:</b> 270\n"
              "│ 🌐 <b>Трафик:</b> ∞ Безлимит\n"
              "│ 💶 <b>Стоимость:</b> 1109₽\n"
              "─────────────────────────────────</blockquote>\n\n"
              "<i>Для продолжения нажмите кнопку ниже</i> 👇"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.continue_to_choose_devices
    )

# Тариф 12 месяцев
@router.callback_query(F.data == '12 месяцев')
async def one_month(callback: CallbackQuery):
    await callback.answer('1 год')

    photo_path = "./assets/1year_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
              "💎 <b>Тариф: 12 месяцев</b>\n"
              "<blockquote>─────────────────────────────────\n"
              "│ 🔖 <b>Описание:</b> Нам Нужно Больше ВЫГОДЫ!\n"
              "│ 🗓  <b>Кол-во Дней:</b> 365\n"
              "│ 🌐 <b>Трафик:</b> ∞ Безлимит\n"
              "│ 💶 <b>Стоимость:</b> 1449₽\n"
              "─────────────────────────────────</blockquote>\n\n"
              "<i>Для продолжения нажмите кнопку ниже</i> 👇"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.continue_to_choose_devices
    )

# Обход тарифы
@router.callback_query(F.data == '7 дней (25 GB)')
async def one_month(callback: CallbackQuery):
    await callback.answer('7 дней')

    photo_path = "./assets/7days_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
              "🥷 <b>Спец-тариф: 7 дней (25 GB)</b>\n\n"
              "<blockquote>─────────────────────────────────\n"
              "│ 🔖 <b>Описание:</b> Минимум затрат — максимум свободы.\n"
              "│ 🗓  <b>Кол-во Дней:</b> 7\n"
              "│ 🌐 <b>Трафик:</b> 25 GB\n"
              "│ 💶 <b>Стоимость:</b> 75₽\n"
              "─────────────────────────────────</blockquote>\n\n"
              "<i>Для продолжения нажмите кнопку ниже</i> 👇"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.continue_to_choose_devices_1
    )

@router.callback_query(F.data == '14 дней (50 GB)')
async def one_month(callback: CallbackQuery):
    await callback.answer('14 дней')

    photo_path = "./assets/14days_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
              "🥷 <b>Спец-тариф: 14 дней (50 GB)</b>\n\n"
              "<blockquote>─────────────────────────────────\n"
              "│ 🔖 <b>Описание:</b> Две недели стабильного доступа.\n"
              "│ 🗓  <b>Кол-во Дней:</b> 14\n"
              "│ 🌐 <b>Трафик:</b> 50 GB\n"
              "│ 💶 <b>Стоимость:</b> 135₽\n"
              "─────────────────────────────────</blockquote>\n\n"
              "<i>Для продолжения нажмите кнопку ниже</i> 👇"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.continue_to_choose_devices_1
    )

@router.callback_query(F.data == '30 дней (100 GB)')
async def one_month(callback: CallbackQuery):
    await callback.answer('30 дней')

    photo_path = "./assets/30days_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
              "🥷 <b>Спец-тариф: 30 дней (100 GB)</b>\n\n"
              "<blockquote>─────────────────────────────────\n"
              "│ 🔖 <b>Описание:</b> Чикибоб 🤝\n"
              "│ 🗓  <b>Кол-во Дней:</b> 30\n"
              "│ 🌐 <b>Трафик:</b> 100 GB\n"
              "│ 💶 <b>Стоимость:</b> 215₽\n"
              "─────────────────────────────────</blockquote>\n\n"
              "<i>Для продолжения нажмите кнопку ниже</i> 👇"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.continue_to_choose_devices_1
    )

@router.callback_query(F.data == '1 месяц (225 GB)')
async def one_month(callback: CallbackQuery):
    await callback.answer('14 дней')

    photo_path = "./assets/14days_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
              "💥 <b>Мульти-тариф: 1 месяц (225 GB)</b>\n\n"
              "<blockquote>─────────────────────────────────\n"
              "│ 🔖 <b>Описание:</b> Месяц полного доступа.\n"
              "│ 🗓  <b>Кол-во Дней:</b> 30\n"
              "│ 🌐 <b>Трафик:</b> 225 GB\n"
              "│ 💶 <b>Стоимость:</b> 219₽\n"
              "─────────────────────────────────</blockquote>\n\n"
              "<i>Для продолжения нажмите кнопку ниже</i> 👇"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.continue_to_choose_devices_2
    )

@router.callback_query(F.data == '3 месяца (675 GB)')
async def one_month(callback: CallbackQuery):
    await callback.answer('14 дней')

    photo_path = "./assets/14days_knight.jpg"
    photo = FSInputFile(photo_path)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=(
              "💥 <b>Мульти-тариф: 3 месяца (675 GB)</b>\n\n"
              "<blockquote>─────────────────────────────────\n"
              "│ 🔖 <b>Описание:</b> 3 месяца полного доступа.\n"
              "│ 🗓  <b>Кол-во Дней:</b> 90\n"
              "│ 🌐 <b>Трафик:</b> 675 GB\n"
              "│ 💶 <b>Стоимость:</b> 639₽\n"
              "─────────────────────────────────</blockquote>\n\n"
              "<i>Для продолжения нажмите кнопку ниже</i> 👇"
            ),
            parse_mode="HTML"
        ),
        reply_markup=kb.continue_to_choose_devices_2
    )