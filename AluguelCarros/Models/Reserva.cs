namespace AluguelCarros.Models
{
    public class Reserva
    {
        public int Id { get; set; }
        public int VeiculoId { get; set; }
        public int ClienteId { get; set; }
        public DateTime DataInicio { get; set; }
        public DateTime DataFim { get; set; }
        public decimal ValorTotal { get; set; }
        public string Status { get; set; } = "Pendente";

        public Veiculo? Veiculo { get; set; }
        public Cliente? Cliente { get; set; }
    }
}