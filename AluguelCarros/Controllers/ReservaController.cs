using AluguelCarros.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.EntityFrameworkCore;

namespace AluguelCarros.Controllers
{
	public class ReservaController : Controller
	{
		private readonly AppDbContext _context;

		public ReservaController(AppDbContext context)
		{
			_context = context;
		}

		// Lista todas as reservas
		public async Task<IActionResult> Index()
		{
			var reservas = await _context.Reservas
				.Include(r => r.Veiculo)
				.Include(r => r.Cliente)
				.ToListAsync();
			return View(reservas);
		}

		// Exibe formulário de nova reserva
		public IActionResult Criar()
		{
			ViewBag.Veiculos = new SelectList(
				_context.Veiculos.Where(v => v.Disponivel), "Id", "Modelo");
			ViewBag.Clientes = new SelectList(
				_context.Clientes, "Id", "Nome");
			return View();
		}

		// Salva a nova reserva
		[HttpPost]
		public async Task<IActionResult> Criar(Reserva reserva)
		{
			if (ModelState.IsValid)
			{
				// Calcula o valor total automaticamente
				var dias = (reserva.DataFim - reserva.DataInicio).Days;
				var veiculo = await _context.Veiculos.FindAsync(reserva.VeiculoId);

				if (veiculo == null || dias <= 0)
				{
					ModelState.AddModelError("", "Veículo inválido ou datas incorretas.");
					return View(reserva);
				}

				reserva.ValorTotal = dias * veiculo.ValorDiaria;
				reserva.Status = "Pendente";

				// Marca o veículo como indisponível
				veiculo.Disponivel = false;

				_context.Reservas.Add(reserva);
				_context.Veiculos.Update(veiculo);
				await _context.SaveChangesAsync();
				return RedirectToAction(nameof(Index));
			}

			ViewBag.Veiculos = new SelectList(
				_context.Veiculos.Where(v => v.Disponivel), "Id", "Modelo");
			ViewBag.Clientes = new SelectList(
				_context.Clientes, "Id", "Nome");
			return View(reserva);
		}

		// Aprova uma reserva
		public async Task<IActionResult> Aprovar(int id)
		{
			var reserva = await _context.Reservas.FindAsync(id);
			if (reserva == null) return NotFound();
			reserva.Status = "Aprovada";
			_context.Reservas.Update(reserva);
			await _context.SaveChangesAsync();
			return RedirectToAction(nameof(Index));
		}

		// Cancela uma reserva e libera o veículo
		public async Task<IActionResult> Cancelar(int id)
		{
			var reserva = await _context.Reservas
				.Include(r => r.Veiculo)
				.FirstOrDefaultAsync(r => r.Id == id);

			if (reserva == null) return NotFound();

			// Libera o veículo novamente
			if (reserva.Veiculo != null)
			{
				reserva.Veiculo.Disponivel = true;
				_context.Veiculos.Update(reserva.Veiculo);
			}

			reserva.Status = "Cancelada";
			_context.Reservas.Update(reserva);
			await _context.SaveChangesAsync();
			return RedirectToAction(nameof(Index));
		}
	}
}