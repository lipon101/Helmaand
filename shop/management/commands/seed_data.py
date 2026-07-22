from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shop.models import Category, Product, Review, Promo
from accounts.models import Profile
from security.models import CTFFlag
from security.ctf_flags import ALL_FLAGS


class Command(BaseCommand):
    help = "Seed the database with demo products, CTF flags, a sample XSS review, and promo codes."

    def handle(self, *args, **options):
        # --- Admin / test users ---
        if not User.objects.filter(username="admin").exists():
            admin_user = User.objects.create_superuser("admin", "admin@helmaand.local", "admin123")
            admin_user.first_name = "Lab"
            admin_user.last_name = "Author"
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created superuser: admin / admin123"))
        else:
            admin_user = User.objects.get(username="admin")

        if not User.objects.filter(username="demo").exists():
            demo = User.objects.create_user("demo", "demo@helmaand.local", "demo123")
            self.stdout.write(self.style.SUCCESS("Created user: demo / demo123"))
        else:
            demo = User.objects.get(username="demo")

        # Ensure profiles exist
        Profile.objects.get_or_create(user=admin_user)
        Profile.objects.get_or_create(user=demo)
        self.stdout.write("User profiles ready.")

        # --- Categories ---
        cat_mens, _ = Category.objects.get_or_create(
            name="Men's Wear",
            defaults={"slug": "mens-wear", "description": "Premium men's clothing collection"},
        )
        cat_womens, _ = Category.objects.get_or_create(
            name="Women's Wear",
            defaults={"slug": "womens-wear", "description": "Elegant women's clothing collection"},
        )
        cat_access, _ = Category.objects.get_or_create(
            name="Accessories",
            defaults={"slug": "accessories", "description": "Fashion accessories and add-ons"},
        )
        self.stdout.write("Categories ready.")

        # --- Active demo products ---
        products_data = [
            ("Luxury Leather Jacket", "luxury-leather-jacket", cat_mens, 299.99, "Premium full-grain leather jacket with a tailored fit.", "Helmaand"),
            ("Silk Evening Gown", "silk-evening-gown", cat_womens, 189.99, "Flowing silk evening gown, perfect for galas.", "Helmaand"),
            ("Gold-Plated Watch", "gold-plated-watch", cat_access, 149.99, "Minimalist gold-plated wristwatch.", "Aurum"),
            ("Cashmere Sweater", "cashmere-sweater", cat_mens, 119.99, "Ultra-soft cashmere knit sweater.", "Nordic Co."),
            ("Designer Sunglasses", "designer-sunglasses", cat_access, 89.99, "UV-protective polarized sunglasses.", "Vision"),
            ("Wool Overcoat", "wool-overcoat", cat_mens, 249.99, "Classic wool blend overcoat.", "Helmaand"),
        ]
        for name, slug, cat, price, desc, brand in products_data:
            Product.objects.get_or_create(
                slug=slug,
                defaults={
                    "category": cat,
                    "name": name,
                    "brand": brand,
                    "description": desc,
                    "price": price,
                    "stock": 15,
                    "is_active": True,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Created {len(products_data)} active products."))

        # --- Hidden flag product (is_active=False) for UNION SQLi ---
        sqli_union_flag = ALL_FLAGS['sqli_union'][0]
        flag_product, created = Product.objects.get_or_create(
            slug="ctf-secret-flag-product",
            defaults={
                "category": cat_access,
                "name": "Secret Admin Item",
                "brand": "CLASSIFIED",
                "description": f"Congratulations! You found the hidden flag: {sqli_union_flag}",
                "price": 0.01,
                "stock": 1,
                "is_active": False,
            },
        )
        if created:
            self.stdout.write(self.style.WARNING(f"Created hidden flag product (is_active=False)."))
        else:
            if sqli_union_flag not in flag_product.description:
                flag_product.description = f"Congratulations! You found the hidden flag: {sqli_union_flag}"
                flag_product.save()
            self.stdout.write("Hidden flag product already exists.")

        # --- Promo codes for time-based SQLi ---
        Promo.objects.update_or_create(
            code="SUMMER25",
            defaults={"discount": 25, "is_active": True},
        )
        Promo.objects.update_or_create(
            code="WELCOME10",
            defaults={"discount": 10, "is_active": True},
        )
        Promo.objects.update_or_create(
            code="VIP50",
            defaults={"discount": 50, "is_active": True},
        )
        self.stdout.write(self.style.SUCCESS("Created promo codes: SUMMER25, WELCOME10, VIP50"))

        # --- Seed all 15 CTF flags into the CTFFlag table ---
        for challenge_id, (flag, category, difficulty) in ALL_FLAGS.items():
            CTFFlag.objects.update_or_create(
                challenge_id=challenge_id,
                defaults={"flag": flag, "category": category, "difficulty": difficulty},
            )
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(ALL_FLAGS)} CTF flags into security_ctfflag table."))

        # --- Sample XSS review (demonstration) ---
        jacket = Product.objects.filter(slug="luxury-leather-jacket").first()
        if jacket and not Review.objects.filter(product=jacket, user=demo).exists():
            Review.objects.create(
                product=jacket,
                user=demo,
                rating=5,
                comment="<b>Great jacket!</b> <script>alert('XSS demo by demo user')</script>",
            )
            self.stdout.write(self.style.WARNING("Created sample XSS review on Luxury Leather Jacket."))

        self.stdout.write(self.style.SUCCESS("Seed complete!"))
        self.stdout.write("")
        self.stdout.write(self.style.HTTP_INFO("── Lab Credentials ──"))
        self.stdout.write("  Admin : admin / admin123")
        self.stdout.write("  Test  : demo  / demo123")
        self.stdout.write("")
        self.stdout.write(self.style.HTTP_INFO("── Flag Format ──"))
        self.stdout.write("  All flags: HLMD{...}")
        self.stdout.write("")
        self.stdout.write(self.style.HTTP_INFO("── Challenges (15) ──"))
        self.stdout.write("  XSS  (5): Stored, Reflected, DOM, Attribute, Self")
        self.stdout.write("  SQLi (5): UNION, Error, Blind, Time-based, Auth Bypass")
        self.stdout.write("  CSRF (5): POST, GET, Login, Logout, Password Change")
