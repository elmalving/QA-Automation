import subprocess
import os
import time
import datetime


class Statistic:
    def __init__(self, file: str, interval: int = 5):
        if interval > 0.4:
            self.interval = interval
        else:
            raise ValueError('Интервал не может быть меньше 0.4, так как программе нужно время на выполнение')
        self.CPU, self.working_set, self.private_bytes, self.handlers = str(), str(), str(), str()
        old_processes = []
        new_processes = []
        processes = subprocess.check_output('tasklist', text=True).split('\n')  # NOQA, через командную строку находит все запущенные процессы в системе
        for process in processes[1:-1]:
            old_processes.append(process)
        os.startfile(file)  # Запускает программу
        time.sleep(2)  # Для браузеров и подобных процессов, которые получают ID не сразу после запуска
        processes = subprocess.check_output('tasklist', text=True).split('\n')  # NOQA, делает тоже самое, что и перед этим, но уже с новым процессом
        for process in processes[1:-1]:
            new_processes.append(process)
        for i in range(len(new_processes)):
            # Ищу разницу между списков процессов
            if i < len(old_processes):
                if old_processes[i].split()[1] != new_processes[i].split()[1]:
                    self.process, self.PID = new_processes[i].split()[:2]
                    break

    def analyze(self):
        try:
            self.handlers, self.CPU, self.private_bytes, self.working_set = subprocess.check_output(
                f'wmic path win32_PerfFormattedData_PerfProc_process where IDProcess={self.PID} get '
                'PercentProcessorTime, WorkingSet, PrivateBytes, HandleCount', text=True).split()[4:]
            # Единственный известный мне способ узнать Private Bytes отдельного процесса используя Python
        except ValueError:
            print('Процесс остановлен')
            exit()
        print(f'CPU usage: {self.CPU}')
        print(f'Working set: {self.working_set}')
        print(f'Private bytes: {self.private_bytes}')
        print(f'Current handlers: {self.handlers}')
        self.save_stats()
        time.sleep(self.interval - 0.4)  # Разница от примерного времени выполнения кода
        self.analyze()

    def save_stats(self):
        with open('stats.txt', 'a') as logs:
            logs.write(f'{datetime.datetime.now().strftime("%m-%d %H:%M:%S")}: CPU: {self.CPU}, Working Set: '
                       f'{self.working_set}, Private Bytes: {self.private_bytes}, Handlers: {self.handlers}\n')


if __name__ == '__main__':
    path = input('Асолютный путь к файлу, который вам нужен: ').replace('\\', '/')
    seconds_wait = int(input('Интервал между сбором статистики: '))
    analyzer = Statistic(path, seconds_wait)
    analyzer.analyze()
