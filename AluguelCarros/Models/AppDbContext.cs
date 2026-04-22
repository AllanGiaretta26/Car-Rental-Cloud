using Microsoft.EntityFrameworkCore;

namespace AluguelCarros.Models
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options)
            : base(options)
        {
        }

        public DbSet<Veiculo> Veiculos { get; set; }
        public DbSet<Cliente> Clientes { get; set; }
        public DbSet<Reserva> Reservas { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<Veiculo>()
                .Property(v => v.ValorDiaria)
                .HasPrecision(10, 2);

            modelBuilder.Entity<Reserva>()
                .Property(r => r.ValorTotal)
                .HasPrecision(10, 2);
        }
    }
}