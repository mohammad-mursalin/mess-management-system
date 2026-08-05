from django.core.management.base import BaseCommand

from apps.cycles.models import Cycle
from apps.members.models import Member, MemberCycle


NAMES = [
    'Muzahid',
    'Saikot',
    'Tamim',
    'Sk.Rony',
    'Tohiduzzaman',
    'Rumen',
    'Rashidul Islam',
    'Prince',
    'Munsur Biswas',
    'Bishal',
    'Rafi',
    'Naim (boro)',
    'Naim (soto)',
    'Shimul',
    'Azmir',
    'Mursalin',
    'Johurul',
    'Abir',
    'Mehedi',
    'Imran vai',
    'Al-Amin',
    'Redoy Hosain',
    'Rahat',
    'Saimon',
    'Sumon',
    'Omor Farukh',
    'Saim',
    'Habib',
    'Saddam (IT)',
    'Asadul',
    'Saddam (boro)',
    'Azizul',
    'Sohag',
    'New Member',
]


class Command(BaseCommand):
    help = 'Seed 34 members into the currently open cycle.'

    def handle(self, *args, **options):
        cycle = Cycle.objects.filter(status='open').first()
        if not cycle:
            self.stderr.write(
                'Error: No open cycle found. Open a cycle first, then re-run this command.'
            )
            return

        self.stdout.write(
            f'Found open cycle: {cycle.label} (start_date={cycle.start_date})'
        )

        created = 0
        skipped = 0

        for name in NAMES:
            existing = Member.objects.filter(
                name=name,
                cycles__cycle=cycle,
            ).first()

            if existing:
                self.stdout.write(
                    self.style.WARNING(f'  SKIP  {name} (already in cycle)')
                )
                skipped += 1
                continue

            member = Member.objects.create(name=name, is_active=True)
            MemberCycle.objects.create(
                member=member,
                cycle=cycle,
                join_date=cycle.start_date,
                deposit_amount=0,
            )
            self.stdout.write(
                self.style.SUCCESS(f'  ADD  {name}')
            )
            created += 1

        total = MemberCycle.objects.filter(cycle=cycle).count()
        self.stdout.write('')
        self.stdout.write('Summary:')
        self.stdout.write(f'  Created : {created}')
        self.stdout.write(f'  Skipped : {skipped}')
        self.stdout.write(f'  Total in cycle: {total}')
        self.stdout.write('Done.')
