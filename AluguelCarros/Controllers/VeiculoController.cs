using AluguelCarros.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Authorization;

namespace AluguelCarros.Controllers
{
    [Authorize]
    public class VeiculoController : Controller
    {
        private readonly AppDbContext _context;

        public VeiculoController(AppDbContext context)
        {
            _context = context;
        }

        // Lista todos os veículos
        public async Task<IActionResult> Index()
        {
            var veiculos = await _context.Veiculos.ToListAsync();
            return View(veiculos);
        }

        // Exibe formulário de cadastro
        public IActionResult Criar()
        {
            return View();
        }

        // Salva o novo veículo no banco
        [HttpPost]
        public async Task<IActionResult> Criar(Veiculo veiculo)
        {
            if (ModelState.IsValid)
            {
                _context.Veiculos.Add(veiculo);
                await _context.SaveChangesAsync();
                return RedirectToAction(nameof(Index));
            }
            return View(veiculo);
        }

        // Exibe formulário de edição
        public async Task<IActionResult> Editar(int id)
        {
            var veiculo = await _context.Veiculos.FindAsync(id);
            if (veiculo == null) return NotFound();
            return View(veiculo);
        }

        // Salva as alterações do veículo
        [HttpPost]
        public async Task<IActionResult> Editar(Veiculo veiculo)
        {
            if (ModelState.IsValid)
            {
                _context.Veiculos.Update(veiculo);
                await _context.SaveChangesAsync();
                return RedirectToAction(nameof(Index));
            }
            return View(veiculo);
        }

        // Exclui o veículo
        public async Task<IActionResult> Excluir(int id)
        {
            var veiculo = await _context.Veiculos.FindAsync(id);
            if (veiculo == null) return NotFound();
            _context.Veiculos.Remove(veiculo);
            await _context.SaveChangesAsync();
            return RedirectToAction(nameof(Index));
        }
    }
}