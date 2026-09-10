import discord
from discord.ext import commands
import os
import re
from datetime import datetime

# --- BOT AYARLARI ---
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# --- ADMIN ID (Kendi Discord ID'ni yaz!) ---
ADMIN_ID = 1532403639115845742  # BURAYA KENDİ ID'NI YAZ!

# --- İZİN VERİLEN SUNUCU ID ---
IZINLI_SUNUCU_ID = 1532403639115845742  # YENİ SUNUCU ID

# --- DOSYA ADI OLUŞTUR ---
def dosya_adi_olustur(site):
    dosya_adi = site.lower().replace(' ', '_').replace('/', '_').replace(':', '_')
    dosya_adi = re.sub(r'[^a-z0-9_.-]', '_', dosya_adi)
    return f"{dosya_adi}.txt"

# --- SUNUCU KONTROL ---
def sunucu_kontrol(ctx):
    """Bot sadece izin verilen sunucuda çalışır"""
    if ctx.guild is None:
        return True
    return ctx.guild.id == IZINLI_SUNUCU_ID

# --- BOT BAŞLADI ---
@bot.event
async def on_ready():
    print(f'✅ Bot hazır! {bot.user}')
    print(f'📊 {len(bot.guilds)} sunucuda aktif')
    print(f'🔒 İzin verilen sunucu ID: {IZINLI_SUNUCU_ID}')
    for guild in bot.guilds:
        if guild.id != IZINLI_SUNUCU_ID:
            await guild.leave()
            print(f'🚪 {guild.name} sunucusundan çıkıldı!')

# --- YENİ SUNUCUYA EKLENİNCE ---
@bot.event
async def on_guild_join(guild):
    if guild.id != IZINLI_SUNUCU_ID:
        await guild.leave()
        print(f'🚪 {guild.name} sunucusundan çıkıldı! (İzinsiz)')
        admin = await bot.fetch_user(ADMIN_ID)
        await admin.send(f"🚫 **{guild.name}** sunucusuna eklendim ama izin verilmediği için çıktım!")

# --- KOMUT ÖNCESİ KONTROL ---
async def komut_kontrol(ctx):
    if not sunucu_kontrol(ctx):
        await ctx.send("❌ Bu bot sadece **belirtilen sunucuda** çalışıyor!")
        return False
    return True

# --- ADMIN KONTROL ---
def is_admin(ctx):
    return ctx.author.id == ADMIN_ID

# --- ADMIN DM GÖNDER ---
async def admin_dm_gonder(ctx, mesaj):
    admin = await bot.fetch_user(ADMIN_ID)
    await admin.send(mesaj)
    await ctx.message.delete()

# --- !hesap_ekle ---
@bot.command()
@commands.check(is_admin)
@commands.check(sunucu_kontrol)
async def hesap_ekle(ctx, site: str = None, *, hesaplar_metni: str = None):
    await ctx.message.delete()
    if site is None:
        await admin_dm_gonder(ctx, "❌ **Site belirt!** Örnek: `!hesap_ekle hesap.com.tr`")
        return
    if hesaplar_metni is None:
        await admin_dm_gonder(ctx, "❌ **Hesap yaz!** Komuttan sonraki satıra hesapları yaz.")
        return
    dosya = dosya_adi_olustur(site)
    if not os.path.exists(dosya):
        with open(dosya, 'w', encoding='utf-8') as f:
            f.write("")
    satirlar = hesaplar_metni.split('\n')
    hesaplar = []
    for satir in satirlar:
        satir = satir.strip()
        if not satir:
            continue
        hesaplar.append(satir)
    if not hesaplar:
        await admin_dm_gonder(ctx, f"❌ Geçerli hesap bulunamadı!")
        return
    with open(dosya, 'a', encoding='utf-8') as f:
        for hesap in hesaplar:
            f.write(f"{hesap}\n")
    await admin_dm_gonder(ctx, f"✅ **{len(hesaplar)}** hesap **{site}** dosyasına eklendi!")

# --- !hesap_sil ---
@bot.command()
@commands.check(is_admin)
@commands.check(sunucu_kontrol)
async def hesap_sil(ctx, site: str = None, email: str = None):
    await ctx.message.delete()
    if site is None or email is None:
        await admin_dm_gonder(ctx, "❌ Örnek: `!hesap_sil hesap.com.tr test@mail.com`")
        return
    dosya = dosya_adi_olustur(site)
    if not os.path.exists(dosya):
        await admin_dm_gonder(ctx, f"❌ '{site}' bulunamadı!")
        return
    with open(dosya, 'r', encoding='utf-8') as f:
        hesaplar = f.read().splitlines()
    yeni_hesaplar = []
    silindi = False
    for hesap in hesaplar:
        if email not in hesap:
            yeni_hesaplar.append(hesap)
        else:
            silindi = True
    with open(dosya, 'w', encoding='utf-8') as f:
        f.write("\n".join(yeni_hesaplar))
    if silindi:
        await admin_dm_gonder(ctx, f"✅ **{site}** silindi: `{email}`")
    else:
        await admin_dm_gonder(ctx, f"❌ Bulunamadı: `{email}`")

# --- !hesap_temizle ---
@bot.command()
@commands.check(is_admin)
@commands.check(sunucu_kontrol)
async def hesap_temizle(ctx, site: str = None):
    await ctx.message.delete()
    if site is None:
        await admin_dm_gonder(ctx, "❌ **Site belirt!** Örnek: `!hesap_temizle hesap.com.tr`")
        return
    dosya = dosya_adi_olustur(site)
    if not os.path.exists(dosya):
        await admin_dm_gonder(ctx, f"❌ '{site}' bulunamadı!")
        return
    with open(dosya, 'r', encoding='utf-8') as f:
        hesaplar = f.read().splitlines()
    hesaplar = [h for h in hesaplar if h.strip()]
    hesap_sayisi = len(hesaplar)
    if hesap_sayisi == 0:
        await admin_dm_gonder(ctx, f"📭 **{site}** zaten boş!")
        return
    with open(dosya, 'w', encoding='utf-8') as f:
        f.write("")
    await admin_dm_gonder(ctx, f"🗑️ **{hesap_sayisi}** hesap **{site}** dosyasından silindi!")

# --- !hesap_tumunu_sil ---
@bot.command()
@commands.check(is_admin)
@commands.check(sunucu_kontrol)
async def hesap_tumunu_sil(ctx):
    await ctx.message.delete()
    dosyalar = [f for f in os.listdir('.') if f.endswith('.txt')]
    if not dosyalar:
        await admin_dm_gonder(ctx, "📭 Hiç dosya yok!")
        return
    toplam = 0
    silinen_dosyalar = []
    for dosya in dosyalar:
        with open(dosya, 'r', encoding='utf-8') as f:
            hesaplar = f.read().splitlines()
        hesaplar = [h for h in hesaplar if h.strip()]
        sayi = len(hesaplar)
        toplam += sayi
        with open(dosya, 'w', encoding='utf-8') as f:
            f.write("")
        silinen_dosyalar.append(f"{dosya} ({sayi} hesap)")
    await admin_dm_gonder(ctx, f"🗑️ **TOPLAM {toplam}** hesap silindi!\n\n📁 Silinen dosyalar:\n" + "\n".join(silinen_dosyalar[:10]))

# --- !log ---
@bot.command()
@commands.check(sunucu_kontrol)
async def log(ctx, site: str = None):
    if not await komut_kontrol(ctx):
        return
    if site is None:
        await ctx.send("❌ **Site belirt!** Örnek: `!log hesap.com.tr`")
        return
    dosya = dosya_adi_olustur(site)
    if not os.path.exists(dosya):
        await ctx.send(f"❌ '{site}' için dosya bulunamadı!")
        return
    with open(dosya, 'r', encoding='utf-8') as f:
        hesaplar = f.read().splitlines()
    hesaplar = [h for h in hesaplar if h.strip()]
    if not hesaplar:
        await ctx.send(f"📭 **{site}** için hesap yok!")
        return
    try:
        hesap_sayisi = len(hesaplar)
        grup_boyutu = 20
        gruplar = [hesaplar[i:i+grup_boyutu] for i in range(0, len(hesaplar), grup_boyutu)]
        for i, grup in enumerate(gruplar, start=1):
            hesap_listesi = "\n".join(grup)
            embed = discord.Embed(
                title=f"🎯 {site.upper()} HESAPLARI",
                description=f"**{hesap_sayisi}** hesap ({i}/{len(gruplar)})",
                color=0x00ff00
            )
            embed.add_field(name="📧 Hesaplar", value=f"```{hesap_listesi}```", inline=False)
            embed.set_footer(text=f"Talep: {ctx.author.name} | {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            await ctx.author.send(embed=embed)
        await ctx.send(f"✅ **{hesap_sayisi} hesap DM'ye gönderildi!** 📩 ({len(gruplar)} mesaj)")
        admin = await bot.fetch_user(ADMIN_ID)
        await admin.send(f"📢 **{ctx.author.name}** `{site}` için **{hesap_sayisi}** hesap istedi!")
    except discord.Forbidden:
        await ctx.send("❌ **DM'lerin kapalı!** Aç ve tekrar dene.")

# --- !hesap_listele ---
@bot.command()
@commands.check(is_admin)
@commands.check(sunucu_kontrol)
async def hesap_listele(ctx, site: str = None):
    await ctx.message.delete()
    if site is None:
        await admin_dm_gonder(ctx, "❌ Örnek: `!hesap_listele hesap.com.tr`")
        return
    dosya = dosya_adi_olustur(site)
    if not os.path.exists(dosya):
        await admin_dm_gonder(ctx, f"❌ '{site}' bulunamadı!")
        return
    with open(dosya, 'r', encoding='utf-8') as f:
        hesaplar = f.read().splitlines()
    hesaplar = [h for h in hesaplar if h.strip()]
    if not hesaplar:
        await admin_dm_gonder(ctx, f"📭 **{site}** için hesap yok!")
        return
    admin = await bot.fetch_user(ADMIN_ID)
    grup_boyutu = 20
    gruplar = [hesaplar[i:i+grup_boyutu] for i in range(0, len(hesaplar), grup_boyutu)]
    for i, grup in enumerate(gruplar, start=1):
        hesap_listesi = "\n".join(grup)
        embed = discord.Embed(
            title=f"📋 {site} HESAP LİSTESİ",
            description=f"**{len(hesaplar)}** hesap ({i}/{len(gruplar)})",
            color=0x00ff00
        )
        embed.add_field(name="Hesaplar", value=f"```{hesap_listesi}```", inline=False)
        await admin.send(embed=embed)

# --- !hesap_sayi ---
@bot.command()
@commands.check(is_admin)
@commands.check(sunucu_kontrol)
async def hesap_sayi(ctx, site: str = None):
    await ctx.message.delete()
    if site is None:
        await admin_dm_gonder(ctx, "❌ Örnek: `!hesap_sayi hesap.com.tr`")
        return
    dosya = dosya_adi_olustur(site)
    if not os.path.exists(dosya):
        await admin_dm_gonder(ctx, f"❌ '{site}' bulunamadı!")
        return
    with open(dosya, 'r', encoding='utf-8') as f:
        hesaplar = f.read().splitlines()
    hesaplar = [h for h in hesaplar if h.strip()]
    await admin_dm_gonder(ctx, f"📊 **{site}** : **{len(hesaplar)}** hesap")

# --- !log_durum ---
@bot.command()
@commands.check(is_admin)
@commands.check(sunucu_kontrol)
async def log_durum(ctx):
    await ctx.message.delete()
    embed = discord.Embed(title="📊 TÜM DOSYALAR", color=0x00ff00)
    dosyalar = [f for f in os.listdir('.') if f.endswith('.txt')]
    if not dosyalar:
        await admin_dm_gonder(ctx, "📭 Hiç dosya yok!")
        return
    toplam = 0
    for dosya in dosyalar:
        with open(dosya, 'r', encoding='utf-8') as f:
            hesaplar = f.read().splitlines()
        hesaplar = [h for h in hesaplar if h.strip()]
        sayi = len(hesaplar)
        toplam += sayi
        site_adi = dosya.replace('.txt', '')
        embed.add_field(name=site_adi, value=f"**{sayi}**", inline=True)
    embed.add_field(name="📊 TOPLAM", value=f"**{toplam}**", inline=False)
    admin = await bot.fetch_user(ADMIN_ID)
    await admin.send(embed=embed)

# --- !yardim ---
@bot.command()
@commands.check(sunucu_kontrol)
async def yardim(ctx):
    if not await komut_kontrol(ctx):
        return
    embed = discord.Embed(
        title="📖 HESAP DAĞITIM BOTU",
        description="Sadece **belirtilen sunucuda** çalışır!",
        color=0x00ff00
    )
    embed.add_field(
        name="!log <site>",
        value="Hesap al\n`!log hesap.com.tr`\n`!log spotify`",
        inline=False
    )
    embed.set_footer(text="Hesaplar DM olarak gönderilir!")
    await ctx.send(embed=embed)

# --- HATA YAKALAMA ---
@hesap_ekle.error
@hesap_sil.error
@hesap_temizle.error
@hesap_tumunu_sil.error
@hesap_listele.error
@hesap_sayi.error
@log_durum.error
async def admin_hata(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.message.delete()

# --- BOTU ÇALIŞTIR ---
bot.run(os.getenv("DISCORD_TOKEN"))