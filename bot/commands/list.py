import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
from datetime import datetime

# =========================
# MODAL FOR INPUT
# =========================
class InputModal(Modal):
    def __init__(self, title: str, label: str, callback):
        super().__init__(title=title)
        self.input_field = TextInput(label=label, required=True)
        self.add_item(self.input_field)
        self.callback = callback  # function to call on submit

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Call the callback (update filters in the parent view)
            await self.callback(interaction, self.input_field.value)

            # Acknowledge silently (no message shown)
            await interaction.response.defer()
        except Exception as e:
            print("Modal submit error:", e)

# =========================
# FILTER BUTTON VIEW
# =========================
class FiltersView(View):
    def __init__(self):
        super().__init__(timeout=300)

        # Initialize filter data
        self.filters = {
            "channels": [],
            "members": [],
            "reactions": [],
            "from_date": None,
            "to_date": None,
        }

        # Dynamic button config: (label, key)
        button_configs = [
            ("Set Channel(s)","Channel(s) separated by commas", "channels"),
            ("Set Member(s)","Member(s) separated by commas", "members"),
            ("Set From Date","From Date [YYYY-MM-DD]", "from_date"),
            ("Set To Date","To Date [YYYY-MM-DD]", "to_date"),
            ("Set Reaction(s)","Reaction(s) separated by commas", "reactions"),
        ]

        # Add input buttons dynamically
        for label,input_label,key in button_configs:
            self.add_item(self.create_input_button(label, input_label, key))

        # Add Submit button with proper callback
        submit_button = Button(label="Submit", style=discord.ButtonStyle.green, custom_id="submit")
        submit_button.callback = self.submit_callback
        self.add_item(submit_button)

    # Create button with dynamic callback
    def create_input_button(self, label, input_label, key):
        button = Button(label=label, style=discord.ButtonStyle.primary, custom_id=key)

        async def button_callback(interaction: discord.Interaction):
            await interaction.response.send_modal(
                InputModal(
                    title=label,
                    label=f"Enter {input_label.lower()}",
                    callback=lambda i, v: self.handle_input(i, v, key)
                )
            )

        button.callback = button_callback
        return button

    # Handle input from modals
    async def handle_input(self, interaction, value, key):
        if key in ["channels", "members", "reactions"]:
            self.filters[key] = [v.strip() for v in value.split(",")]
        elif key in ["from_date", "to_date"]:
            try:
                self.filters[key] = datetime.fromisoformat(value)
            except ValueError:
                await interaction.response.send_message(
                    f"❌ Invalid date format for {key}. Use YYYY-MM-DD",
                    ephemeral=True
                )
        else:
            self.filters[key] = value

    # Callback for Submit button
    async def submit_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Selected Filters", color=discord.Color.blue())

        # Channels
        embed.add_field(
            name="Channel(s)",
            value="\n".join(f"({i+1}) #{channel}" for i, channel in enumerate(self.filters["channels"])) or "[]",
            inline=False
        )

        # Members
        embed.add_field(
            name="Member(s)",
            value="\n".join(f"({i+1}) @{member}" for i, member in enumerate(self.filters["members"])) or "[]",
            inline=False
        )

        # Reactions
        embed.add_field(
            name="Reaction(s)",
            value=", ".join(self.filters["reactions"]) or "[]",
            inline=False
        )

        # Dates
        embed.add_field(
            name="From Date",
            value=self.filters["from_date"].strftime("%Y-%m-%d") if self.filters["from_date"] else "Not set",
            inline=False
        )
        embed.add_field(
            name="To Date",
            value=self.filters["to_date"].strftime("%Y-%m-%d") if self.filters["to_date"] else "Not set",
            inline=False
        )

        embed.set_footer(text=f"Requested by: {interaction.user.name}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

# =========================
# COMMAND
# =========================
@commands.command()
async def list(ctx):
    view = FiltersView()
    embed = discord.Embed(
        title="Select Filters",
        description="Use the buttons below to set filters, then click Submit to see the selected filters.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=view, ephemeral=True)
