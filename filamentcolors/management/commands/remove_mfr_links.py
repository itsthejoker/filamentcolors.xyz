from django.core.management.base import BaseCommand

from filamentcolors.models import Swatch, Manufacturer


class Command(BaseCommand):
    help = "Mark all swatches belonging to a manufacturer as unavailable."

    def handle(self, *args, **options):
        try:
            mfr_name = input(
                "Enter the name of the manufacturer to mark as unavailable: "
            )
            mfr = Manufacturer.objects.filter(name__icontains=mfr_name)
            if mfr.count() == 0:
                self.stdout.write("No manufacturers found with that name.")
                return
            elif mfr.count() > 1:
                self.stdout.write("Multiple manufacturers found with that name.")
                self.stdout.write("Is one of these what you were looking for?")
                for count, m in enumerate(mfr):
                    self.stdout.write(f"{count} - {m.name}")

                choice = input(
                    "Enter the number of the manufacturer you want to remove: "
                )
                try:
                    choice = int(choice)
                except ValueError:
                    self.stdout.write("Invalid input.")
                    return
                if choice > mfr.count() - 1:
                    self.stdout.write("Invalid input.")
                    return
                mfr = mfr[choice]
            else:
                mfr = mfr[0]

            swatches = Swatch.objects.filter(manufacturer=mfr)
            if swatches.count() == 0:
                self.stdout.write("No swatches found for that manufacturer.")
                return

            self.stdout.write(f"Found {swatches.count()} swatches for {mfr.name}.")
            choice = input("Are you sure you want to remove them? (y/n): ")
            if choice.lower() == "y":
                swatches.update(amazon_purchase_link=None, mfr_purchase_link=None)
                self.stdout.write("Swatch(es) removed.")
            else:
                self.stdout.write("Swatch(es) not removed.")
        except KeyboardInterrupt:
            self.stdout.write("\nExiting.")
            return
