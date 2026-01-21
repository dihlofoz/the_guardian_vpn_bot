@router.callback_query(F.data == 'profile')
async def profile(callback: CallbackQuery):
    await callback.answer('Ваш профиль👤')

    tg_id = callback.from_user.id
    full_name = callback.from_user.full_name
    username = callback.from_user.username or "—"

    user_data = await rm.get_user_by_telegram_id(tg_id)

    caption = (
        f"<blockquote>🛡️ <b>Профиль пользователя</b></blockquote>\n\n"
        f"👤 <b>Имя:</b> {full_name}\n"
        f"🆔 <b>Username:</b> @{username}\n\n"
    )

    # --- Извлекаем подписки из панели ---
    raw_users = user_data.get("users") if user_data else None
    user_list = [u for u in raw_users if u.get("telegramId") == tg_id] if raw_users else []

    # Если нет НИ ОДНОЙ подписки
    if not user_list:
        caption += (
            "<blockquote>🚫 <b>Активных подписок не найдено.</b>\n"
            "<b>Получите пробный ключ или оформите подписку</b>💎</blockquote>"
        )
    else:
        # Утилиты
        from datetime import datetime
        fmt = lambda d: datetime.fromisoformat(d.replace("Z", "+00:00")).strftime("%d.%m.%Y") if d else "—"
        to_gb = lambda b: round(b / 1024**3, 2)

        # --- Разделяем по типам подписок ---
        paid_trial = []
        special = []

        for u in user_list:
            desc = u.get("description", "")
            prefix = desc.split()[0] if desc else ""

            if prefix in ("Paid", "Trial"):
                paid_trial.append(u)
            elif prefix == "Special":
                special.append(u)

        # --- Функция выбора самой новой подписки ---
        def pick_latest(subs):
            if not subs:
                return None
            return max(subs, key=lambda s: s.get("expireAt") or "")

        paid_trial_sub = pick_latest(paid_trial)
        special_sub = pick_latest(special)

        # --- Получаем названия тарифов ---
        paid_trial_plan_name = await hp.get_latest_plan_name(tg_id)
        special_plan_name = await hp.get_latest_special_plan_name(tg_id)

        # =====================================================================
        #                         БЛОК PAID / TRIAL
        # =====================================================================
        caption += "<blockquote>✍️ <b>Платная / Пробная подписка:</b>\n\n"

        if not paid_trial_sub:
            caption += "🚫 <b>Активных подписок не найдено.</b>\n</blockquote>\n"
        else:
            u = paid_trial_sub

            start_str = fmt(u.get("createdAt"))
            end_str = fmt(u.get("expireAt"))
            used_bytes = u.get("userTraffic", {}).get("usedTrafficBytes", 0)
            used_gb = to_gb(used_bytes)
            limit_bytes = u.get("trafficLimitBytes", 0)
            traffic_str = f"{used_gb} / {to_gb(limit_bytes)} ГБ" if limit_bytes else f"{used_gb} / ∞"

            status_raw = u.get("status", "—").upper()
            if status_raw == "ACTIVE":
                status = "🟢 Active"
            elif status_raw == "EXPIRED":
                status = "🔴 Expired"
            else:
                status = "⚪️ —"

            sub_link = u.get("subscriptionUrl") or "—"
            plan_name = paid_trial_plan_name or u.get("description", "—")

            caption += (
                f"💎 <b>Тариф:</b> {plan_name}\n\n"
                f"📌 <b>Статус:</b> {status}\n"
                f"🕒 <b>Начало:</b> {start_str}\n"
                f"⏳ <b>Окончание:</b> {end_str}\n"
                f"📦 <b>Трафик:</b> {traffic_str}\n\n"
                f"🔗 <b>Подписка:</b> {sub_link}\n"
                "</blockquote>\n"
            )

        # =====================================================================
        #                         БЛОК SPECIAL
        # =====================================================================
        caption += "<blockquote>✍️ <b>Обход Whitelists подписка:</b>\n\n"

        if not special_sub:
            caption += "🚫 <b>Активных подписок не найдено.</b>\n</blockquote>"
        else:
            u = special_sub

            start_str = fmt(u.get("createdAt"))
            end_str = fmt(u.get("expireAt"))
            used_bytes = u.get("userTraffic", {}).get("usedTrafficBytes", 0)
            used_gb = to_gb(used_bytes)
            limit_bytes = u.get("trafficLimitBytes", 0)
            traffic_str = f"{used_gb} / {to_gb(limit_bytes)} ГБ" if limit_bytes else f"{used_gb} / ∞"

            status_raw = u.get("status", "—").upper()
            if status_raw == "ACTIVE":
                status = "🟢 Active"
            elif status_raw == "EXPIRED":
                status = "🔴 Expired"
            else:
                status = "⚪️ —"

            sub_link = u.get("subscriptionUrl") or "—"
            plan_name = special_plan_name or "Special"

            caption += (
                f"💎 <b>Тариф:</b> {plan_name}\n\n"
                f"📌 <b>Статус:</b> {status}\n"
                f"🕒 <b>Начало:</b> {start_str}\n"
                f"⏳ <b>Окончание:</b> {end_str}\n"
                f"📦 <b>Трафик:</b> {traffic_str}\n\n"
                f"🔗 <b>Подписка:</b> {sub_link}\n"
                "</blockquote>"
            )

    photo = FSInputFile("./assets/profile_knight.jpg")
    await callback.message.edit_media(
        media=InputMediaPhoto(media=photo, caption=caption, parse_mode="HTML"),
        reply_markup=kb.profile_logic
    )